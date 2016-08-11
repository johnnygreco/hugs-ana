#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from astropy.table import Table
plt.style.use('jpg')

groups = [3765, 8453]

results_dir = '../results/'

fig, ax = plt.subplots(1,1)
cmap = plt.get_cmap('rainbow')

for g in groups:
    gdir = results_dir+'group_'+str(g)+'/'
    all = Table.read(gdir+'master_cat.txt', format='ascii')
    sel = Table.read(gdir+'selection_cat.txt', format='ascii')
    viz = Table.read(gdir+'viz_cat.txt', format='ascii')
    ax.scatter(viz['ISO0'], viz['SIGMA'], c='r', s=30)
    ax.scatter(sel['ISO0'], sel['SIGMA'], c=cmap(0.0), alpha=0.3, s=20)
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Isophotal Area [pixel$^2$]')
ax.set_ylabel('$\Sigma$')

try: import RaiseWindow
except: pass
plt.show()
