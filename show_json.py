"""Explained in README.
File dirty.
"""

from pprint import pprint
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import constants as con
import tools

print("> Loading game")
ename, egidx = sys.argv[1:]
egidx = int(egidx)
codf = tools.load_codf(ename, egidx)
ginfo = con.GAMES[(ename, egidx)]
a = np.asarray(codf[["x", "y", "x"]])
a0 = a
print(a.shape)

# print("filtering by coord")
# xref, yref, delta = -500, -500, 310 # train
# xref, yref, delta = -2500, -500, 600 # vertigo
# mask = (
#     (a[:, 0] >= xref - delta) &
#     (a[:, 0] <= xref + delta) &
#     (a[:, 1] >= yref - delta) &
#     (a[:, 1] <= yref + delta)
# )
# print(mask.shape, mask.mean())
# a = a[mask]
# print(a.shape)

print("> Decimating coords")
# a = np.unique(np.around(a.reshape(-1, 3) / 5) * 5, axis=0)
# a = np.unique(np.around(a.reshape(-1, 3) / 10) * 10, axis=0)
# a = np.unique(np.around(a.reshape(-1, 3) / 20) * 20, axis=0)
a = np.unique(np.around(a.reshape(-1, 3) / 40) * 40, axis=0)
a1 = a
print(a.shape)

print("> Plotting")
fig = plt.figure()
ax = fig.gca(projection='3d')

ax.scatter(a[:, 0], a[:, 1], a[:, 2])
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')

ptp = a.ptp(axis=0).max()
cx, cy, cz = a.mean(axis=0)
ax.set_xlim3d([cx - ptp / 2, cx + ptp / 2])
ax.set_ylim3d([cy - ptp / 2, cy + ptp / 2])
ax.set_zlim3d([cz - ptp / 2, cz + ptp / 2])

plt.show()
