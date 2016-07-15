#!/usr/bin/env python 

from astropy.convolution import Ring2DKernel, convolve
from pyraf import iraf

imdir = '../data/HSC/'
imfile = 'deepCoadd_HSC-I_9348_8-6.fits'

iraf.rmedian(imdir+imfile+'[1]', imdir+'filtered.fits')
