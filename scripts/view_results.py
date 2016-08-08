#!/usr/bin/env python 

from astropy.table import Table

import sexpy
import hugs
from toolbox.utils import ds9view

full_cat = True

band, tract, patch, args = hugs.parser.parse_args()
relpath = 'HSC-'+band+'/'+str(tract)+'/'+patch[0]+'-'+patch[-1]

sexin = '../SExIO/sexin/'+relpath+'/'
sexout = '../SExIO/sexout/'+relpath+'/'
imgfile = sexin+'img.fits'

run_label = 'HSC-'+band+'_'+str(tract)+'_'+patch
regfile = '../results/'+run_label+'.reg'

if full_cat:
    cat = Table.read('../results/'+run_label+'_full_cat.txt', format='ascii')
else:
    cat = Table.read('../results/'+run_label+'.txt', format='ascii')
sexpy.cat_to_ds9reg(cat, outfile=regfile, textparam=args.text_param)

ds9view(imgfile, regfile)
