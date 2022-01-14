#%%
import numpy as np
import multiprocessing as mp
import networkx as nx
import pandas as pd
import os
import time
import json
import matplotlib.pyplot as plt

#%%
##--------------- READ CONFIGURATION FILE ----------------##
##--------------------------------------------------------##

with open("../config.json", 'r') as f:
    config = json.load(f)

deep_graph_analysis = config['deep_graph_analysis']
directed_graph = config['directed_graph']
weighted_graph = config['weighted_graph']
clustering = config['clustering']
day = config['day']
fraction_samples = config['fraction_samples']

num_cpus = config['num_cpus']
if num_cpus==0:
    num_cpus = 2*mp.cpu_count()
elif num_cpus==-1:
    num_cpus = mp.cpu_count()-1

#%%
##---------------------- READ FILE -----------------------##
##--------------------------------------------------------##

file_path = "../data/DASH-"+day+"/merged.txt"
transactions = pd.read_csv(file_path, sep = '\s+')

output_path = './'+day

#%%
##----------------- MAP PUBLIC KEY TO ID -----------------##
##--------------------------------------------------------##

nodes = pd.concat([transactions['Key-sender'], transactions['Key-receiver']]).unique()

nodes_dict = {address:i for i,address in enumerate(nodes)}

transactions['id_sender'] = [nodes_dict[address] for address in transactions['Key-sender']]
transactions['id_receiver'] = [nodes_dict[address] for address in transactions['Key-receiver']]

#%%
##------------------- BUILD DATA GRAPH -------------------##
##--------------------------------------------------------##

if weighted_graph:
    output_path += '_weighted'
    transactions_weighted = transactions.groupby(transactions.columns.tolist(), as_index=False).size()
    if directed_graph:
        output_path += '_directed'
        data_graph = nx.from_pandas_edgelist(transactions_weighted, 'id_sender', 'id_receiver', 'size', create_using=nx.DiGraph)
    else:
        data_graph = nx.from_pandas_edgelist(transactions, 'id_sender', 'id_receiver', create_using=nx.Graph)
else:
    if directed_graph:
        output_path += '_directed'
        data_graph = nx.from_pandas_edgelist(transactions, 'id_sender', 'id_receiver', create_using=nx.DiGraph)
    else:
        data_graph = nx.from_pandas_edgelist(transactions, 'id_sender', 'id_receiver', create_using=nx.Graph)

n_nodes_data = data_graph.number_of_nodes()
n_edges_data = data_graph.number_of_edges()

print("Created graph for the day {}.".format(day))
if directed_graph:
    print("The graph is directed")
else:
    print("The graph is undirected")
if weighted_graph:
    print("The graph is weighted")
else:
    print("The graph is unweighted")
print("Number of nodes of data graph: {}".format(n_nodes_data))
print("Number of edges of data graph: {}\n".format(n_edges_data))


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
                         'weighted': weighted_graph,},
            'number_of_nodes': n_nodes_data,
            'number_of_edges': n_edges_data,
            'clustering_coefficient':None,
            'num_cpus': [],
            'sample_size': [],
            'time':[],
            'ASPL': []}

#%%
##----------------- DEGREE DISTRIBUTIONS -----------------##
##--------------------------------------------------------##

if deep_graph_analysis:
    def degree_distribution(degree, title, yscale = 'linear', n_bins = 100): 
        plt.hist(degree, bins=n_bins)
        plt.yscale(yscale)
        plt.title(d + " distribution")
        plt.show()

    degree = [val for (node, val) in data_graph.degree()]
    in_degree = [val for (node, val) in data_graph.in_degree()]
    out_degree = [val for (node, val) in data_graph.out_degree()]

    degree_dict = {'Total degree' : degree, 'In degree' : in_degree, 'Out degree': out_degree}

    for d in degree_dict:
        degree_distribution(degree_dict[d], d, yscale = 'log')


# %%
##---------------- CLUSTERING COEFFICIENT ----------------##
##--------------------------------------------------------##

if clustering:
    clust_coeff_data = nx.average_clustering(data_graph)
    print("Clustering coefficient of data graph: {:.8f}\n".format(clust_coeff_data))

    data['clustering_coefficient'] = clust_coeff_data

# %%
##------------------- MAIN COMPONENTS --------------------##
##--------------------------------------------------------##

if directed_graph:
    main_comp_data = data_graph.subgraph(max(nx.weakly_connected_components(data_graph), key=len)).copy()

else:
    components = sorted([c for c in nx.connected_components(data_graph)], key=len, reverse=True)
    main_comp_data = data_graph.subgraph(components[0])
    
# %%
##---------------- AVERAGE SHORTEST PATH -----------------##
##--------------------------------------------------------##

def ASPL(nodes, graph, return_dict, procnum):
    """
    Compute average shortest path length for directed graph.
    """
    tot_links = 0.0
    tot_SPL = 0.0
    
    
    for source in nodes:
        
        n_links = 0.0
        SPL = 0.0
        
        for target in graph.nodes():
            if nx.has_path(graph, source, target) and source != target:
                n_links += 1
                SPL += nx.shortest_path_length(graph, source, target)
        
        tot_links += n_links
        tot_SPL += SPL    
    
    return_dict[procnum] = (tot_SPL, tot_links)

#%%
##--------------------- ASPL DATA ------------------------##
##--------------------------------------------------------##ù

for fs in fraction_samples:
    
    print("Starting ASPL for a fraction of {} of the sample".format(fs))
    
    start = time.time()

    mc_data_sample = main_comp_data.subgraph(
        np.random.choice(main_comp_data.nodes(), int(fs*len(main_comp_data.nodes())))
        )
    
    nodes = np.array(mc_data_sample.nodes(), dtype='int')

    nodes_for_subprocess = np.array_split(nodes, num_cpus)
    
    process_list = []
    
    manager = mp.Manager()
    return_dict = manager.dict()
    
    for i in range(num_cpus):

        p = mp.Process(target=ASPL, args=[nodes_for_subprocess[i], 
                                          mc_data_sample,
                                          return_dict,
                                          i])
        p.start()
        process_list.append(p)
        
    for p in process_list:
        p.join()
        
    tot_SPL = sum([x[0] for x in return_dict.values()])
    tot_links = sum([x[1] for x in return_dict.values()])
    ASPL_data = tot_SPL/tot_links
    
    print("Number of nodes: {}".format(len(mc_data_sample)))
    print("Number of cpus used: {}".format(num_cpus))
    print("Time required: {:.2f} seconds".format(time.time()-start))
    print("ASPL: {:.2f}\n".format(ASPL_data))

    data['num_cpus'].append(num_cpus)
    data['sample_size'].append(len(mc_data_sample))
    data['time'].append(time.time()-start)
    data['ASPL'].append(ASPL_data)
    
    with open(output_path + '.json', 'w') as f:
        f.write(json.dumps(data))
