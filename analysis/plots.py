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