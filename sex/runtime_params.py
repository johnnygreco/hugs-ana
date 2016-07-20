
checkimg_names = 'sex_bckgrd.fits,sex_filter.fits,sex_aps.fits,sex_seg.fits,sex_objs.fits'
checkimg_type = 'BACKGROUND,FILTERED,APERTURES,SEGMENTATION,OBJECTS'

config = {'PARAMETERS_NAME' : 'myparams',
          'FILTER'          : 'Y',
          'THRESH_TYPE'     : 'RELATIVE',
          'DEBLEND_NTHRESH' : 16,
          'DEBLEND_MINCONT' : 0.01,
          'DETECT_MINAREA'  : 800,
          'DETECT_THRESH'   : 1.,
          'ANALYSIS_THRESH' : 1.,
          'BACK_SIZE'       : 100.0,
          'BACK_FILTERSIZE' : 3,
          'CLEAN'           : 'Y',
          'CLEAN_PARAM'     : 0.1,
          'MAG_ZEROPOINT'   : 27.0,
          'PIXEL_SCALE'     : 0.168,
          'SEEING_FWHM'     : 0.7,
          'WEIGHT_IMAGE'    : 'wts_bad.fits',
          'WEIGHT_TYPE'     : 'MAP_WEIGHT',
          'WEIGHT_THRESH'   : 0.0,
          'PHOT_APERTURES'  : '3,4,5,6,7,8,16,32',
          'PHOT_FLUXFRAC'   : 0.5,
          'PHOT_AUTOAPERS'  : '5.0,5.0',
          'CHECKIMAGE_NAME' : checkimg_names, 
          'CHECKIMAGE_TYPE' : checkimg_type
          }
