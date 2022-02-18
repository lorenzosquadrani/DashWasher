#%%
import numpy as np
import multiprocessing as mp
import networkx as nx
import pandas as pd
import os
import time
import json
import sys
from argparse import ArgumentParser

parser = ArgumentParser()

# get day argument
parser.add_argument("-c", "--config", dest="config", type=str, help="configuration file path")
parser.add_argument("-d", "--day", dest="day", type=str, help="day")

args = parser.parse_args()

if args.config:
    config_path = args.config
else:
    sys.exit("Please give a configuration file")

if args.day:
    day = args.day
else:
    sys.exit("Please give a day")


#%%
##--------------- READ CONFIGURATION FILE ----------------##
##--------------------------------------------------------##


with open(config_path, 'r') as f:
    config = json.load(f)

directed_graph = config['directed_graph']
weighted_graph = config['weighted_graph']
clustering = config['clustering']
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


#%%
##---------------------- READ FILE -----------------------##
##--------------------------------------------------------##

file_path = "./data/merged_data/"+day+"_merged.txt"
transactions = pd.read_csv(file_path, sep = '\s+')

output_path = './results/'+day

#%%
##----------------- MAP PUBLIC KEY TO ID -----------------##
##--------------------------------------------------------##

nodes = pd.concat([transactions['Key-sender'], transactions['Key-receiver']]).unique()

nodes_dict = {address:i for i,address in enumerate(nodes)}

transactions['id_sender'] = [nodes_dict[address] for address in transactions['Key-sender']]
transactions['id_receiver'] = [nodes_dict[address] for address in transactions['Key-receiver']]

# no self-loops
transactions = transactions[transactions.id_sender != transactions.id_receiver]


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

output_path += '_transactions'

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
            'num_links': [],
            'time':[],
            'ASPL': []}


# %%
##---------------- CLUSTERING COEFFICIENT ----------------##
##--------------------------------------------------------##

if clustering:

    clust_coeff_data = nx.average_clustering(data_graph)
    print("Clustering coefficient of data graph: {:.8f}\n".format(clust_coeff_data))
    data['clustering_coefficient'] = clust_coeff_data


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


#%%
##--------------------- ASPL DATA ------------------------##
##--------------------------------------------------------##ù

for fs in fraction_samples:

    print("Starting ASPL for a fraction of {} of the sample".format(fs))

    start = time.time()

    num_nodes = int(fs*len(data_graph.nodes()))

    rng = np.random.default_rng()
    chosen_nodes = rng.choice(data_graph.nodes, num_nodes, replace=False)
    subsample = data_graph.subgraph(chosen_nodes)

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
    ASPL_data = tot_SPL/tot_paths

    print("Number of nodes: {}".format(len(subsample)))
    print("Number of paths: {}".format(int(tot_paths)))
    print("Number of cpus used: {}".format(num_cpus))
    print("Time required: {:.2f} seconds".format(time.time()-start))
    print("ASPL: {:.3f}\n".format(ASPL_data))

    data['num_cpus'].append(num_cpus)
    data['sample_size'].append(len(subsample))
    data['num_links'].append(int(tot_paths))
    data['time'].append(time.time()-start)
    data['ASPL'].append(ASPL_data)

    with open(output_path + '.json', 'w') as f:
        f.write(json.dumps(data))
