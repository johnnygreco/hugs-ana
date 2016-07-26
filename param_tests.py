#!/usr/bin/env python 

"""
Messy little script for experimenting... 
"""
import argparse
from sex import runsex, kernals, config, apply_cuts
from toolbox.utils import ds9view, read_sexout, sexout_to_ds9reg

######################################################
# Argument Parser
######################################################
parser = argparse.ArgumentParser()
parser.add_argument('tract', type=str, default='9348')
parser.add_argument('patch', type=str, default='7-6')
parser.add_argument('-t', '--textparam', help='text parameter for ds9', 
                    type=str, default='MU_MAX')
parser.add_argument('-r', '--run_it', help='run search', action='store_true')
parser.add_argument('-k', '--kernal', nargs=3, default=['gauss', 9, 5.0],
                    help='kernal: name, size, width_param')
args = parser.parse_args()

######################################################
# Set parameters
######################################################
band = 'I'
tract = args.tract
patch = args.patch[0]+'-'+args.patch[-1]
imfile = 'img.fits'
kern_name = args.kernal[0]
size = int(args.kernal[1])
width_param = float(args.kernal[2])
convfile = kernals.exp(size, width_param, write=True)
kern = {'gauss':kernals.gauss, 'exp':kernals.exp}[kern_name]
convfile = kern(size, width_param, write=True)

######################################################
# Modify config parameters
######################################################
checkimg_names = 'sex-background.fits,sex-filtered.fits,'
checkimg_names += 'sex-apertures.fits,sex-seg.fits,sex-objects.fits'
checkimg_type = 'BACKGROUND,FILTERED,APERTURES,SEGMENTATION,OBJECTS'
config['FILTER_NAME'] = convfile
config['CHECKIMAGE_NAME'] = checkimg_names
config['CHECKIMAGE_TYPE'] = checkimg_type

######################################################
# Run SExtractor if -r arg given
######################################################
relpath = 'HSC-'+band+'/'+tract+'/'+patch[0]+'-'+patch[-1]+'/'
if args.run_it:
    runsex(imfile, cat='sex.cat', relpath=relpath, **config)

######################################################
# Make cuts on catalog
######################################################
sexin = 'sexin/'+relpath
sexout = 'sexout/'+relpath
table = read_sexout(sexout+'sex.cat')
table = apply_cuts(table)

######################################################
# Make ds9 reg file and view results with ds9
######################################################
regfile = sexout+'sex.reg'
sexout_to_ds9reg(table, textparam=args.textparam, outfile=regfile)
ds9view(sexin+imfile, regfile)
