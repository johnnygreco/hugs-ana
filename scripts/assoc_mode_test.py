#!/usr/bin/env python 

import numpy as np
from astropy.io import fits
import sexpy
from hugs.parser import parse_args

# get command-line arguments
args = parse_args()
tract, patch = args.tract, args.patch
relpath = 'HSC-I/'+str(tract)+'/'+patch[0]+'-'+patch[-1]

do_steps = [1,1,1,1,1,1]

params = ['X_IMAGE', 'Y_IMAGE', 'MAG_AUTO']

if do_steps[0]:
    config = {'DETECT_THRESH':10.0,
              'BACK_SIZE':128}
    sw = sexpy.SexWrapper(config, params, relpath=relpath)
    sw.set_check_images(['s', 'b', 'brms'], prefix='bright-1-')
    print('executing step 1...')
    print('current config:')
    for k, v in sw.get_config().items():
        print(k, v)
    sw.run(cat='bright-1.cat')

    # subtract the bg from image
    img = fits.open(sw.get_indir('img.fits'))[0]
    bg = fits.getdata(sw.get_outdir('bright-1-BACKGROUND.fits'))
    img_bg_sub = 'img_bg_sub.fits'
    header = img.header
    print('writing', sw.get_indir(img_bg_sub))
    fits.writeto(sw.get_indir(img_bg_sub), img.data-bg, header,
            clobber=True)

if do_steps[1]:
    #################################################
    # Reconfigure to ASSOC mode with previous cat
    # as the association catalog. Use low threshold.
    #################################################
    config = {'BACK_TYPE'       : 'MANUAL', 
              'ASSOC_NAME'      : 'bright-1.cat',
              'ASSOC_PARAMS'    : '1,2,3',
              'ASSOC_TYPE'      : 'MAG_MEAN',
              'ASSOC_RADIUS'    : 5.0, 
              'ASSOC_DATA'      : '1,2,3',
              'ASSOCSELEC_TYPE' : 'MATCHED', 
              'DETECT_THRESH'   : 0.7}
    sw = sexpy.SexWrapper(config, params, relpath=relpath)
    sw.set_check_images(['s'], prefix='assoc-1-')
    sw.add_param(['VECTOR_ASSOC('+str(i)+')' for i in range(1,4)])
    sw.run(img_bg_sub, cat='assoc-1.cat')

if do_steps[2]:
    # replace detections from step 2 with sky noise
    config = {'BACK_TYPE'       : 'MANUAL', 
              'DETECT_THRESH'   : 0.7}
    sw = sexpy.SexWrapper(config, relpath=relpath)
    segmap = fits.getdata(sw.get_outdir('assoc-1-SEGMENTATION.fits'))
    rms = fits.getdata(sw.get_outdir('bright-1-BACKGROUND_RMS.fits'))
    skynoise = rms*np.random.randn(rms.shape[0], rms.shape[1])
    img = fits.open(sw.get_indir('img_bg_sub.fits'))[0]
    img.data[segmap!=0] = skynoise[segmap!=0]
    clean_img = 'img_bg_sub_clean-1.fits'
    fits.writeto(sw.get_indir(clean_img), img.data, img.header, clobber=True)
    sw.set_check_images(['a','s'], prefix='clean-1-')
    sw.run(clean_img, cat='clean-1.cat')

if do_steps[3]:
    config = {'BACK_TYPE' : 'MANUAL',
              'DETECT_THRESH':6.0}
    sw = sexpy.SexWrapper(config, params, relpath=relpath)
    sw.set_check_images(['s'], prefix='bright-2-')
    sw.run('img_bg_sub_clean-1.fits', cat='bright-2.cat')

if do_steps[4]:
    config = {'BACK_TYPE'       : 'MANUAL', 
              'ASSOC_NAME'      : 'bright-2.cat',
              'ASSOC_PARAMS'    : '1,2,3',
              'ASSOC_TYPE'      : 'MAG_MEAN',
              'ASSOC_RADIUS'    : 5.0, 
              'ASSOC_DATA'      : '1,2,3',
              'ASSOCSELEC_TYPE' : 'MATCHED', 
              'DETECT_THRESH'   : 1.0}
    sw = sexpy.SexWrapper(config, params, relpath=relpath)
    sw.set_check_images(['s'], prefix='assoc-2-')
    sw.add_param(['VECTOR_ASSOC('+str(i)+')' for i in range(1,4)])
    sw.run('img_bg_sub_clean-1.fits', cat='assoc-2.cat')

if do_steps[5]:
    config = {'BACK_TYPE'       : 'MANUAL', 
              'DETECT_THRESH'   : 0.7}
    sw = sexpy.SexWrapper(config, relpath=relpath)
    sw.make_kernal('gauss', 31, 25.0)
    segmap = fits.getdata(sw.get_outdir('assoc-2-SEGMENTATION.fits'))
    rms = fits.getdata(sw.get_outdir('bright-1-BACKGROUND_RMS.fits'))
    skynoise = rms*np.random.randn(rms.shape[0], rms.shape[1])
    img = fits.open(sw.get_indir('img_bg_sub_clean-1.fits'))[0]
    img.data[segmap!=0] = skynoise[segmap!=0]
    clean_img = 'img_bg_sub_clean-2.fits'
    fits.writeto(sw.get_indir(clean_img), img.data, img.header, clobber=True)
    sw.set_check_images(['a','s'], prefix='clean-2-')
    print('executing step 6...')
    print('current config:')
    for k, v in sw.get_config().items():
        print(k, v)
    sw.run(clean_img, cat='clean-2.cat')
