import pandas as pd
import networkx as nx
import numpy as np
import time
import os

#%%
##---------------------- READ FILE -----------------------##
##--------------------------------------------------------##

file_path = "../data/DASH-2021-01-01/merged.txt"

transactions = pd.read_csv(file_path, sep = '\s+')

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

data_graph = nx.from_pandas_edgelist(transactions, 'id_sender', 'id_receiver', create_using=nx.DiGraph)


# %%
##------------------- MAIN COMPONENT ---------------------##
##--------------------------------------------------------##

main_comp_data = data_graph.subgraph(max(nx.weakly_connected_components(data_graph), key=len)).copy()

# %%
##---------------- AVERAGE SHORTEST PATH -----------------##
##--------------------------------------------------------##

def ASPL(graph):
    """
    Compute average shortest path length for directed graph.
    """

    tot_links = 0.0
    tot_SPL = 0.0

    for source in graph.nodes():
        n_links = 0.0
        SPL = 0.0
        for target in graph.nodes():
            if nx.has_path(graph, source, target) and source != target:
                n_links += 1
                SPL += nx.shortest_path_length(graph, source, target)

        tot_links += n_links
        tot_SPL += SPL
    
    ASPL = tot_SPL/tot_links
    return ASPL

#%%
##--------------------- ASPL DATA ------------------------##
##--------------------------------------------------------##

if os.path.isdir('./results_ASPL_directed/'):
    print("Found already existing folder for the results. Trying to read old data and append new ones.")
    data_samplesize_list = list(np.load('./results_ASPL_directed/subsample_size.npy'))
    data_time_list       = list(np.load('./results_ASPL_directed/elapsed_time.npy')) 
    data_ASPL_list       = list(np.load('./results_ASPL_directed/aspl.npy'))
    
    
else:
    os.mkdir('results_ASPL_directed')
    data_samplesize_list = []
    data_time_list       = []
    data_ASPL_list       = []
    
fraction_samples = [0.01,0.05,0.1,0.15,0.2]

for fs in fraction_samples:
    mc_data_sample = main_comp_data.subgraph(np.random.choice(main_comp_data.nodes(), int(fs*len(main_comp_data.nodes()))))

    start = time.time()
    ASPL_data = ASPL(mc_data_sample)
    
    data_time_list.append(time.time()-start)
    data_samplesize_list.append(len(mc_data_sample))
    data_ASPL_list.append(ASPL_data)
    
    print(len(mc_data_sample), time.time()-start, ASPL_data)
    np.save('./results_ASPL_directed/subsample_size.npy', np.array(data_samplesize_list))
    np.save('./results_ASPL_directed/elapsed_time.npy'  , np.array(data_time_list))
    np.save('./results_ASPL_directed/aspl.npy'          , np.array(data_ASPL_list))
    
