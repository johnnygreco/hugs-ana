
checkimg_names = 'sex-background.fits,sex-filtered.fits,'
checkimg_names += 'sex-apertures.fits,sex-seg.fits,sex-objects.fits'
checkimg_type = 'BACKGROUND,FILTERED,APERTURES,SEGMENTATION,OBJECTS'

config = {'PARAMETERS_NAME' : 'myparams',
          'FILTER'          : 'Y',
          'THRESH_TYPE'     : 'RELATIVE',
          'MAG_ZEROPOINT'   : 27.0,
          'PIXEL_SCALE'     : 0.168,
          'SEEING_FWHM'     : 0.7,
          'WEIGHT_IMAGE'    : 'wts_bad.fits',
          'WEIGHT_TYPE'     : 'MAP_WEIGHT',
          'WEIGHT_THRESH'   : 0.0,
          'PHOT_FLUXFRAC'   : 0.5,
          'CHECKIMAGE_NAME' : checkimg_names, 
          'CHECKIMAGE_TYPE' : checkimg_type,
          }
