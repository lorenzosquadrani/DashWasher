import pandas as pd
import multiprocessing as mp
import networkx as nx
import numpy as np
import time
import os
import json

fraction_samples = [0.02,0.07,0.1,0.2,0.25,0.3,0.4,0.5 ]



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
##--------------------------------------------------------##


if not os.path.isdir('./results/'):
    print("Created folder '/results'")
    os.mkdir('results')

if os.path.isfile('./results/data_dict.json'):
    print("Found already existing results. Trying to read old data and append new ones.")
    
    with open('./results/data_dict.json') as f:
        data = json.loads(f.read())
else:
    data = {'metadata': [],
            'sample_size': [],
            'time':[],
            'ASPL': []}

start = time.time()
for fs in fraction_samples:
    
    
    mc_data_sample = main_comp_data.subgraph(
        np.random.choice(main_comp_data.nodes(), int(fs*len(main_comp_data.nodes())))
        )

    nodes = np.array(mc_data_sample.nodes(), dtype='int')
    num_cpus = mp.cpu_count()
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
    
    print(len(mc_data_sample), time.time()-start, ASPL_data)
    
    data['metadata'].append({'num_cpus':num_cpus,
                             'weighted':False,})
    data['sample_size'].append(len(mc_data_sample))
    data['time'].append(time.time()-start)
    data['ASPL'].append(ASPL_data)
    
    with open('./results/data_dict.json', 'w') as f:
        f.write(json.dumps(data))
    
