
#%%
import numpy as np
import multiprocessing as mp
import networkx as nx
import pandas as pd
import os
import time
import json
import matplotlib.pyplot as plt


# %%
##------------------ BUILD RANDOM GRAPH ------------------##
##--------------------------------------------------------##

if build_rnd:
    link_probability = n_edges_data/(n_nodes_data*(n_nodes_data - 1))

    if link_probability < 1e-3:
        random_graph = nx.fast_gnp_random_graph(n_nodes_data, link_probability, directed=True)
    else:
        random_graph = nx.gnp_random_graph(n_nodes_data, link_probability, directed=True)

    n_nodes_random = random_graph.number_of_nodes()
    n_edges_random = random_graph.number_of_edges()

    print("Number of nodes of random graph: ", n_nodes_random)
    print("Number of edges of random graph: ", n_edges_random)


main_comp_random = random_graph.subgraph(max(nx.weakly_connected_components(random_graph), key=len)).copy()

clust_coeff_random = nx.average_clustering(random_graph)
print("Clustering coefficient of random graph: {}".format(clust_coeff_random))