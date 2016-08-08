#!/usr/bin/env python

import os

import hugs
import pipeline
from sexpy import SEX_IO_DIR 

sexin = os.path.join(SEX_IO_DIR, 'sexin')
tracts = os.listdir(os.path.join(sexin, 'HSC-I'))

for t in tracts: 
    tdir = os.path.join(os.path.join(sexin, 'HSC-I'), t) 
    patches = os.listdir(tdir)
    for p in patches:
        relpath = 'HSC-I/'+t+'/'+p
        run_label = 'HSC-I'+'_'+t+'_'+p
        pipeline.main(relpath, run_label, results_dir='../results')
