import json
import matplotlib.pyplot as plt
import numpy as np
import datetime
import pandas

with open("../results/MP_dilena_2021-01-01.json") as f:

        data_mp = json.loads(f.read())
        
        
with open("../results/2021-01-01_directed_nx_mp.json") as f:

        data_mp_nx = json.loads(f.read())
        
     

# FIGURE 1
        
fig, ax = plt.subplots(figsize=(10,8))

num_nodes = data_mp_nx['number_of_nodes']


x = np.array(data_mp['sample_size'])
x_ord = x[x.argsort()] /num_nodes

y = np.array(data_mp['time'])
y_ord = y[x.argsort()]/3600

ax.plot(x_ord, y_ord,  'o--',label='DiLeNA',)

x = np.array(data_mp_nx['sample_size'])
x_ord = x[x.argsort()] / num_nodes

y = np.array(data_mp_nx['time'])
y_ord = y[x.argsort()]/3600

ax.plot(x_ord, y_ord ,'o--', label='New version')


ax.set_yscale('log')


ax.set_xlabel('fraction of nodes', fontsize=20)
ax.set_ylabel('computational time (hours)', fontsize=20)

ax.grid()
ax.legend(fontsize=20)

ax.tick_params(axis='both', labelsize=15)

fig.savefig('performances_1.jpg')



# FIGURE 2

fig, ax = plt.subplots(figsize=(10,8))

num_nodes = data_mp_nx['number_of_nodes']


x = np.array(data_mp['sample_size'])
x_ord = x[x.argsort()] /num_nodes

y = np.array(data_mp['ASPL'])
y_ord = y[x.argsort()]

ax.plot(x_ord, y_ord,  'o--',label='DiLeNA',)

x = np.array(data_mp_nx['sample_size'])
x_ord = x[x.argsort()] / num_nodes

y = np.array(data_mp_nx['ASPL'])
y_ord = y[x.argsort()]

ax.plot(x_ord, y_ord ,'o--', label='New version')


ax.set_xlabel('fraction of nodes', fontsize=20)
ax.set_ylabel('ASPL', fontsize=20)

ax.grid()
ax.legend(fontsize=20)

ax.tick_params(axis='both', labelsize=15)

fig.savefig('performances_2.jpg')