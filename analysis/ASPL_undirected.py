import numpy as np
import networkx as nx
import pandas as pd
import os
import time

file_path = "../data/DASH-2021-01-01/merged.txt"
transactions = pd.read_csv(file_path, sep = '\s+')

nodes = pd.concat([transactions['Key-sender'], transactions['Key-receiver']]).unique()

nodes_dict = {address:i for i,address in enumerate(nodes)}

transactions['id_sender'] = [nodes_dict[address] for address in transactions['Key-sender']]
transactions['id_receiver'] = [nodes_dict[address] for address in transactions['Key-receiver']]

data_graph = nx.from_pandas_edgelist(transactions, 'id_sender', 'id_receiver', create_using=nx.Graph)

print("Created graph. Starting subsampling...")

components = sorted([c for c in nx.connected_components(data_graph)], key=len, reverse=True)
main_component = data_graph.subgraph(components[0])

if os.path.isdir('./results_ASPL_undirected/'):
    print("Found already existing folder for the results. Trying to read old data and append new ones.")
    subsample_size = list(np.load('./results_ASPL_undirected/subsample_size.npy'))
    elapsed_time = list(np.load('./results_ASPL_undirected/elapsed_time.npy'))
    aspl = list(np.load('./results_ASPL_undirected/aspl.npy'))
else:
    os.mkdir('results_ASPL_undirected')
    subsample_size = []
    elapsed_time = []
    aspl = []

num_nodes = [33000,34000,35000,36000]

for n in num_nodes:
    
    nodes = np.random.choice(main_component.nodes(), size=n)
    subsample = main_component.subgraph(nodes)
    components = sorted([c for c in nx.connected_components(subsample)], key=len, reverse=True)
    subsample = subsample.subgraph(components[0])
    
    subsample_size.append(len(subsample))
    
    start = time.time()
    aspl_data = nx.average_shortest_path_length(subsample)
    elapsed_time.append(time.time()- start)
    
    aspl.append(aspl_data)
    print(n, len(subsample), time.time()-start, aspl_data)
    np.save('./results_ASPL_undirected/subsample_size.npy',np.array(subsample_size))
    np.save('./results_ASPL_undirected/elapsed_time.npy',np.array(elapsed_time))
    np.save('./results_ASPL_undirected/aspl.npy',np.array(aspl))
