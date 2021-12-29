#%%
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import random
import numpy as np
import time

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

weighted_graph = False

if weighted_graph:
    transactions_weighted = transactions.groupby(transactions.columns.tolist(), as_index=False).size()
    data_graph = nx.from_pandas_edgelist(transactions_weighted, 'id_sender', 'id_receiver', 'size', create_using=nx.DiGraph)
else:
    data_graph = nx.from_pandas_edgelist(transactions, 'id_sender', 'id_receiver', create_using=nx.DiGraph)

n_nodes_data = data_graph.number_of_nodes()
n_edges_data = data_graph.number_of_edges()

print("Number of nodes of data graph: ", n_nodes_data)
print("Number of edges of data graph: ", n_edges_data)

#%%
##----------------- DEGREE DISTRIBUTIONS -----------------##
##--------------------------------------------------------##

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
##------------------ BUILD RANDOM GRAPH ------------------##
##--------------------------------------------------------##

link_probability = n_edges_data/(n_nodes_data*(n_nodes_data - 1))

if link_probability < 1e-3:
    random_graph = nx.fast_gnp_random_graph(n_nodes_data, link_probability, directed=True)
else:
    random_graph = nx.gnp_random_graph(n_nodes_data, link_probability, directed=True)

n_nodes_random = random_graph.number_of_nodes()
n_edges_random = random_graph.number_of_edges()

print("Number of nodes of random graph: ", n_nodes_random)
print("Number of edges of random graph: ", n_edges_random)

# %%
##---------------- CLUSTERING COEFFICIENT ----------------##
##--------------------------------------------------------##

clust_coeff_data = nx.average_clustering(data_graph)
clust_coeff_random = nx.average_clustering(random_graph)

print("Clustering coefficient of data graph: {}".format(clust_coeff_data))
print("Clustering coefficient of random graph: {}".format(clust_coeff_random))

# %%
##------------------- MAIN COMPONENTS --------------------##
##--------------------------------------------------------##

fraction_sample = 0.01

main_comp_data = data_graph.subgraph(max(nx.weakly_connected_components(data_graph), key=len)).copy()
main_comp_random = random_graph.subgraph(max(nx.weakly_connected_components(random_graph), key=len)).copy()

mc_data_sample = main_comp_data.subgraph(np.random.choice(main_comp_data.nodes(), int(fraction_sample*len(main_comp_data.nodes()))))
mc_random_sample = main_comp_random.subgraph(np.random.choice(main_comp_random.nodes(), int(fraction_sample*len(main_comp_random.nodes()))))

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

data_time_list = []
data_ASPL_list = []
fraction_samples = [0.01, 0.05, 0.1, 0.15, 0.25]

for fs in fraction_samples:
    mc_data_sample = main_comp_data.subgraph(np.random.choice(main_comp_data.nodes(), int(fs*len(main_comp_data.nodes()))))

    start = time.time()
    ASPL_data = ASPL(mc_data_sample)

    data_time_list.append(time.time()-start)
    data_ASPL_list.append(ASPL_data)

#%%
##--------------------- ASPL RANDOM ----------------------##
##--------------------------------------------------------##

start = time.time()

ASPL_random = ASPL(mc_random_sample)

print(" # of nodes: {}\n ASPL: {}\n Time: {}".format(mc_random_sample.number_of_nodes(), ASPL_random, time.time()-start))

# %%
