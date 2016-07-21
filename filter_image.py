#!/usr/bin/env python 

from imtools import rmedian

imdir = 'sexin/HSC-I/9590/1-4/'
imfile = imdir+'img.fits'
rmedian(imfile, imdir+'rmedian.fits', 5, 7)
