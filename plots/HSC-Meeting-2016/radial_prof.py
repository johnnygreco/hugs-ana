#!/usr/bin/env python 

import numpy as np
import matplotlib.pyplot as plt
from astropy.table import Table

results_dir = '../../results/'
groups = [1925, 3765, 4736, 6112, 8453]

for g in groups:
    fn = results_dir+'group_'+str(g)+'/viz_cat.txt'
    tab = Table.read(fn, format='ascii')
    


