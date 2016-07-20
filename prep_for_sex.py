#!/usr/bin/env python 

"""
Prepare images for SExtractor.
"""

from __future__ import print_function

import os
from utils import prep_for_sex

imdir = 'sexin/HSC-I'

tracts = os.listdir(imdir)

for t in tracts:
    patches = os.listdir(os.path.join(imdir, t))
    for p in patches:
        prep_for_sex(t, p)
