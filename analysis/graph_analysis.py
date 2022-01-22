#%%
import numpy as np
import multiprocessing as mp
import networkx as nx
import pandas as pd
import os
import time
import json
import sys
import matplotlib.pyplot as plt

#%%
##--------------- READ CONFIGURATION FILE ----------------##
##--------------------------------------------------------##

config_path = "../config.json"

with open(config_path, 'r') as f:
    config = json.load(f)

directed_graph = config['directed_graph']
weighted_graph = config['weighted_graph']
clustering = config['clustering']
day = config['day']
fraction_samples = config['fraction_samples']

#%%
##---------------------- READ FILE -----------------------##
##--------------------------------------------------------##

file_path = "../data/merged_data/"+day+"_merged.txt"
transactions = pd.read_csv(file_path, sep = '\s+')

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
    transactions_weighted = transactions.groupby(transactions.columns.tolist(), as_index=False).size()
    if directed_graph:
        data_graph = nx.from_pandas_edgelist(transactions_weighted, 'id_sender', 'id_receiver', 'size', create_using=nx.DiGraph)
    else:
        data_graph = nx.from_pandas_edgelist(transactions, 'id_sender', 'id_receiver', create_using=nx.Graph)
else:
    if directed_graph:
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
    degree_distribution(degree_dict[d], d, yscale='log')
