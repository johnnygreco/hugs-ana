#!/usr/bin/env python 

"""
Prepare images for SExtractor.
"""

from __future__ import print_function

import os
from sex import imprep

imdir = 'sexin/HSC-I'

tracts = [t for t in os.listdir(imdir) if t[0]!='.']

for t in tracts:
    pdir = os.path.join(imdir, t)
    patches = [p for p in os.listdir(pdir) if p[0]!='.']
    for p in patches:
        imprep.prep_for_sex(t, p)
