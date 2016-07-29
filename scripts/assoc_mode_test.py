#!/usr/bin/env python 

import numpy as np
from astropy.io import fits
import sexpy
from hugs.parser import parse_args

# get command-line arguments
args = parse_args()
tract, patch = args.tract, args.patch
relpath = 'HSC-I/'+str(tract)+'/'+patch[0]+'-'+patch[-1]

#################################################
# setup initial SExtractor wrapper object
# goal: detect really bright things 
#################################################

config = {'DETECT_THRESH' : 10.0, 
          'DETECT_MINAREA': 5}
params = ['X_IMAGE', 'Y_IMAGE', 'MAG_AUTO']

sw = sexpy.SexWrapper(config, params, relpath=relpath)
sw.set_check_images(['s'], prefix='bright_')

# run SEXtractor
sw.run('img.fits', cat='bright.cat')

#################################################
# Reconfigure to ASSOC mode with previous cat
# as the association catalog. Use low threshold.
# goal: generate deep seg map to use as mask.
#################################################

config = {'ASSOC_NAME'      : 'bright.cat',
          'ASSOC_PARAMS'    : '1,2,3',
          'ASSOC_TYPE'      : 'MAG_MEAN',
          'ASSOC_RADIUS'    : 5.0, 
          'ASSOC_DATA'      : '1,2,3',
          'ASSOCSELEC_TYPE' : 'MATCHED', 
          'DETECT_THRESH'   : 0.7}
          
sw.set_config(**config)
sw.set_check_images('s', prefix='assoc_')
sw.add_param(['VECTOR_ASSOC('+str(i)+')' for i in range(1,4)])
sw.run('img.fits', cat='assoc.cat')
