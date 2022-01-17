#%%
import numpy as np
import multiprocessing as mp
import networkx as nx
import pandas as pd
import os
import time
import json
import matplotlib.pyplot as plt
import sys

#%%
##--------------- READ CONFIGURATION FILE ----------------##
##--------------------------------------------------------##

config_path = sys.argv[1]

with open(config_path, 'r') as f:
    config = json.load(f)

deep_graph_analysis = config['deep_graph_analysis']
directed_graph = config['directed_graph']
weighted_graph = config['weighted_graph']
clustering = config['clustering']
day = config['day']
fraction_samples = config['fraction_samples']

if config['num_cpus']!= 1:
    print("Parallel cpu processing not implemented yet. Using just one.")

num_cpus = 1


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

if os.path.isfile(output_path+'_nx.json'):
    print("Found already existing results. Trying to read old data and append new ones.\n")
    
    with open(output_path+'_nx.json') as f:
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

#%%
##--------------------- ASPL DATA ------------------------##
##--------------------------------------------------------##

for fs in fraction_samples:
    
    print("Starting ASPL for a fraction of {} of the sample".format(fs))
    
    start = time.time()

    chosen_nodes = np.random.choice(data_graph.nodes(), int(fs*len(data_graph.nodes())))
    
    subsample = main_comp_data.subgraph(chosen_nodes)

    if directed_graph:
        subsample = subsample.subgraph(max(nx.weakly_connected_components(subsample), key=len)).copy()
    else:
        subsample = subsample.subgraph(max(nx.connected_components(subsample), key=len)).copy()

    ASPL_data = nx.average_shortest_path_length(subsample)
    
    print("Number of nodes: {}".format(len(subsample)))
    print("Number of cpus used: {}".format(num_cpus))
    print("Time required: {:.2f} seconds".format(time.time()-start))
    print("ASPL: {:.2f}\n".format(ASPL_data))

    data['num_cpus'].append(num_cpus)
    data['sample_size'].append(len(subsample))
    data['time'].append(time.time()-start)
    data['ASPL'].append(ASPL_data)
    
    with open(output_path + '_nx.json', 'w') as f:
        f.write(json.dumps(data))
