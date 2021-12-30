import numpy as np
import matplotlib.pyplot as plt

x = np.load('results_ASPL_directed/subsample_size.npy')
y = np.load('results_ASPL_directed/elapsed_time.npy')
z = np.load('results_ASPL_directed/aspl.npy')

order = np.argsort(x)

fig, ax = plt.subplots(figsize=(10,5))

ax.plot(x[order], y[order]/60,'o--', label ='computation time')
ax.set_ylabel('Computation Time (min)')
ax.legend()

ax2 = ax.twinx()
ax2.plot(x[order], z[order],'o--', label='aspl', color='orange')
ax2.legend()

fig.savefig('x.png')