#%%
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

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

transactions_weighted = transactions.groupby(transactions.columns.tolist(), as_index=False).size()
data_graph = nx.from_pandas_edgelist(transactions_weighted, 'id_sender', 'id_receiver', 'size', create_using=nx.DiGraph)

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
