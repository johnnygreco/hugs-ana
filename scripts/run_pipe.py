#!/usr/bin/env python 
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np

import toolbox
import hugs

# detect bright sources
step_1 = {'DETECT_THRESH'    : 10.0,
          'BACK_SIZE'        : 128,
          'set_check_images' : ['b', 'brms'],
          'params'           : ['X_IMAGE', 'Y_IMAGE', 'MAG_AUTO']}

# find faint sources associated with bright sources
step_2 = {#'BACK_TYPE'        : 'MANUAL',
          'ASSOC_NAME'       : 'bright.cat',
          'ASSOC_PARAMS'     : '1,2,3',
          'ASSOC_TYPE'       : 'MAG_MEAN',
          'ASSOC_RADIUS'     : 2.0,
          'ASSOC_DATA'       : '1,2,3',
          'ASSOCSELEC_TYPE'  : 'MATCHED',
          'DETECT_THRESH'    : 1.0,
          'set_check_images' : 's',
          'params'           : ['X_IMAGE', 'Y_IMAGE','MAG_AUTO']+\
                               ['VECTOR_ASSOC('+str(i)+')' for i in range(1,4)]}
 
# find faint sources not associated with bright sources
step_3 = {#'BACK_TYPE'        : 'MANUAL',
          'DETECT_THRESH'    : 0.7, 
          'CLEAN_PARAM'      : 5,
          'set_check_images' : 'a'}

pipe_steps = [(1, 'bright', step_1),
              (1, 'assoc', step_2),
              (1, 'clean', step_3)]

######################################################
# Get command-line args and run pipeline
######################################################

results_dir = '../results'
band, tract, patch, = hugs.parser.parse_args(HSC_info=True)
relpath = 'HSC-'+band+'/'+str(tract)+'/'+patch[0]+'-'+patch[-1]
run_label = 'HSC-'+band+'_'+str(tract)+'_'+patch
hugs.pipeline.run(relpath, pipe_steps, run_label, results_dir=results_dir,
        ds9reg=True, view_with_ds9=True, clean=False)
