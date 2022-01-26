
#%%
import numpy as np
import multiprocessing as mp
import networkx as nx
import pandas as pd
import os
import time
import json
import sys

#%%
##--------------- READ CONFIGURATION FILE ----------------##
##--------------------------------------------------------##

config_path = sys.argv[1]

with open(config_path, 'r') as f:
    config = json.load(f)

directed_graph = config['directed_graph']
weighted_graph = config['weighted_graph']
formula_ASPL = config['formula_ASPL']
days = config['day']
fraction_samples = config['fraction_samples']

num_cpus = config['num_cpus']
if num_cpus==0:
    num_cpus = mp.cpu_count()
    num_processes = 2 * num_cpus
elif num_cpus==-1:
    num_cpus = mp.cpu_count()
    num_processes = num_cpus - 1
else:
    num_processes = num_cpus
    
    
if weighted_graph:
    print("Weighted version not implemented. Ignoring...")
    
for day in days:
    #%%
    ##---------------------- READ FILE -----------------------##
    ##--------------------------------------------------------##

    file_path = "./results/" + day +"_" 
    if directed_graph:
        file_path+="directed"
    file_path += "_nx_mp.json"

    with open(file_path) as f:
        data = json.loads(f.read())

    n_nodes = data['number_of_nodes']
    n_edges = data['number_of_edges']

    output_path = './results/random_'+day


    # %%
    ##------------------ BUILD RANDOM GRAPH ------------------##
    ##--------------------------------------------------------##

    link_probability = n_edges/(n_nodes*(n_nodes - 1))

    if link_probability < 1e-3:
        random_graph = nx.fast_gnp_random_graph(n_nodes, link_probability, directed=True)
    else:
        random_graph = nx.gnp_random_graph(n_nodes, link_probability, directed=True)

    n_nodes_random = random_graph.number_of_nodes()
    n_edges_random = random_graph.number_of_edges()

    print("Created Random Graph for day {}.".format(day))
    print("Number of nodes of random graph: ", n_nodes_random)
    print("Number of edges of random graph: ", n_edges_random)



    #%%
    ##---------------------- PREPARE OUTPUT FILE -----------------------##
    ##------------------------------------------------------------------##

    if os.path.isfile(output_path+'.json'):
        print("Found already existing results. Trying to read old data and append new ones.\n")

        with open(output_path+'.json') as f:
            data = json.loads(f.read())

    else:
        data = {'metadata': {'day': day,
                             'directed': directed_graph,
                             'weighted': weighted_graph},
                'number_of_nodes': n_nodes_random,
                'number_of_edges': n_edges_random,
                'clustering_coefficient':None,
                'num_cpus': [],
                'num_links': [],
                'time':[],
                'ASPL': []}

    # %%
    ##---------------- CLUSTERING COEFFICIENT ----------------##
    ##--------------------------------------------------------##

    clust_coeff = nx.average_clustering(random_graph)
    print("Clustering coefficient of data graph: {:.8f}\n".format(clust_coeff))
    data['clustering_coefficient'] = clust_coeff


    # %%
    ##---------------- AVERAGE SHORTEST PATH -----------------##
    ##--------------------------------------------------------##

    def ASPL(nodes, graph, return_dict, procnum):

        tot_paths = 0.
        tot_SPL = 0.

        for source in nodes:        
            paths = nx.single_source_shortest_path_length(graph, source)

            tot_paths += len(paths)-1
            tot_SPL += sum(paths.values())

        return_dict[procnum] = (tot_SPL, tot_paths)


    def ASPL_formula(n_nodes, n_edges):
        L = 0.5 + (np.log(n_nodes)-0.57722)/np.log(n_edges/n_nodes)
        return L

    #%%
    ##--------------------- ASPL DATA ------------------------##
    ##--------------------------------------------------------##ù

    if not formula_ASPL:
        for fs in fraction_samples:

            print("Starting ASPL for a fraction of {} of the sample".format(fs))

            start = time.time()

            num_nodes = int(fs*len(random_graph.nodes()))

            rng = np.random.default_rng()
            chosen_nodes = rng.choice(random_graph.nodes, num_nodes, replace=False)
            subsample = random_graph.subgraph(chosen_nodes)

            nodes = np.array(subsample.nodes(), dtype='int')

            nodes_for_subprocess = np.array_split(nodes, num_processes)

            process_list = []

            manager = mp.Manager()
            return_dict = manager.dict()

            for i in range(num_processes):

                p = mp.Process(target=ASPL, args=[nodes_for_subprocess[i], 
                                                  subsample,
                                                  return_dict,
                                                  i])
                p.start()
                process_list.append(p)

            for p in process_list:
                p.join()

            tot_SPL = sum([x[0] for x in return_dict.values()])
            tot_paths = sum([x[1] for x in return_dict.values()])
            ASPL = tot_SPL/tot_paths

            print("Number of cpus used: {}".format(num_cpus))
            print("Time required: {:.2f} seconds".format(time.time()-start))
            print("ASPL: {:.3f}\n".format(ASPL))

            data['num_cpus'].append(num_cpus)
            data['num_links'].append(int(tot_paths))
            data['time'].append(time.time()-start)
            data['ASPL'].append(ASPL)

    else:
        ASPL = ASPL_formula(n_nodes_random, n_edges_random)
        
        print("ASPL computed through the formula: {:.3f}\n".format(ASPL))
        
        data['num_cpus'].append(0)
        data['num_links'].append(0)
        data['time'].append(0)
        data['ASPL'].append(ASPL)

    print("-"*20)
    with open(output_path + '.json', 'w') as f:
        f.write(json.dumps(data))

    