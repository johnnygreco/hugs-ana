#!/usr/bin/env python 

"""
Prepare images for SExtractor.
"""

from __future__ import print_function

import os
from sex import imprep

groups = True

if groups:
    group_id = 3765

    imdir = 'sexin/group_'+str(group_id)+'/'
    sigfiles = [f for f in os.listdir(imdir) if 'sig' in f]
    
    for f in sigfiles:
        prefix = imdir+f[:-8]
        wfile = prefix+'wts.fits' 
        imprep.sig_to_wts(imdir+f, wfile, sexpath=False)
        bfile = prefix+'bad.fits'
        wnewfile = prefix+'wts_bad.fits'
        imprep.wts_with_badpix(wfile, bfile, wnewfile, sexpath=False)
else:
    imdir = 'sexin/HSC-I'
    tracts = [t for t in os.listdir(imdir) if t[0]!='.']
    for t in tracts:
        pdir = os.path.join(imdir, t)
        patches = [p for p in os.listdir(pdir) if p[0]!='.']
        for p in patches:
            imprep.prep_for_sex(t, p)
