"""
SExtractor configurations for each pipeline step.
"""

# detect bright sources
step_1 = {'DETECT_THRESH'    : 6.0,
          'BACK_SIZE'        : 128, 
          'set_check_images' : (['s', 'b', 'brms'], 'bright-')}

step_2 = {'BACK_TYPE'       : 'MANUAL', 
          'ASSOC_NAME'      : 'bright-1.cat',
          'ASSOC_PARAMS'    : '1,2,3',
          'ASSOC_TYPE'      : 'MAG_MEAN',
          'ASSOC_RADIUS'    : 5.0, 
          'ASSOC_DATA'      : '1,2,3',
          'ASSOCSELEC_TYPE' : 'MATCHED', 
          'DETECT_THRESH'   : 0.7}

pipe_steps = [('bright', step_1), 
              ('assoc', step_2)]
