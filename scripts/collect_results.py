#!/usr/bin/env python 

import os
from astropy.table import Table, vstack
import hugs
from sexpy import SEX_IO_DIR

sexin = os.path.join(SEX_IO_DIR, 'sexin')
tracts = os.listdir(os.path.join(sexin, 'HSC-I'))

cat = Table()

for t in tracts:
    tdir = os.path.join(os.path.join(sexin, 'HSC-I'), t)
    patches = os.listdir(tdir)
    for p in patches:
        relpath = 'HSC-I/'+t+'/'+p
        run_label = 'HSC-I'+'_'+t+'_'+p
        tempcat = Table.read('../results/'+run_label+'.txt', format='ascii')
        tempcat['tract'] = [int(t)]*len(tempcat)
        tempcat['patch'] = [p]*len(tempcat)
        cat = vstack([cat, tempcat])

cat.write('../results/final_test_cat.txt', format='ascii')
