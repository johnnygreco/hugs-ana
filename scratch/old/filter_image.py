#!/usr/bin/env python 

from imtools import rmedian

imdir = 'sexin/HSC-I/9348/7-6/'
imfile = imdir+'img.fits'
rmedian(imfile, '/Users/protostar/Desktop/rmedian.fits', 12, 14)
