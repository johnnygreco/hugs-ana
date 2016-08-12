#!/usr/bin/env python 

"""
Find all Yang 2007 galaxies and associated groups
within a specified ra, dec, and z. Also, calculate the 
angular diameter distance and save as a csv file for 
Xzavier.
Note to self: write some data fetching functions! 
"""

import numpy as np
from astropy.table import Table, vstack
from toolbox.cosmo import Cosmology
catDIR = '../data/catalogs/'
h=0.7; omegaM0=0.3; omegaL0=0.7
cosmo = Cosmology(h, omegaM0, omegaL0)

################### cuts 
# (note position cuts apply to center of group)
ra_range = [212., 216.]
dec_range = [51.6, 53.5]
Ngal_range = [4, 15] 
zmax = 0.08
#ra_range = [170, 194]
#dec_range = [-1.8, 1.38]
#Ngal_range = [2, 3] 
#zmax = 0.025
################### 

yang = Table.read(catDIR+'Yang/yang_modelC_all.txt', format='ascii')

# cut on the number of galaxies
cut  = (yang['Ngal']>=Ngal_range[0]) & (yang['Ngal']<=Ngal_range[1])  
yang = yang[cut]
yang.remove_column('gal_id')
yang.remove_column('vagc_id')
yang.remove_column('Mh_Lest')
yang.remove_column('Mh_Mest')
yang.remove_column('Mr')
yang.remove_column('g-r')

# need to sort by group id for yang group indexing
yang.sort('group_id') 

# get group info
group = np.loadtxt(catDIR+'/Yang/group_DR7/modelC_group', skiprows=3, usecols=(0,1,2,3))
group = Table([group[:,i] for i in range(group.shape[1])],
               names=('group_id', 'ra', 'dec', 'z'), dtype=(int, 'f8', 'f8', 'f8'))

# match galay member and group catalogs via indexing of group file
group = group[yang['group_id']-1]
yang['ra_c'] = group['ra']
yang['dec_c'] = group['dec']
yang['z_c'] = group['z']

# cut on ra, dec, and redshift of group center
cut  = (yang['ra_c']>=ra_range[0]) & (yang['ra_c']<=ra_range[1]) 
cut &= (yang['dec_c']>=dec_range[0]) & (yang['dec_c']<=dec_range[1]) 
cut &= (yang['z_c']<zmax) 
yang = yang[cut]

# calculate the angular diameter distances for the center of group
D_A = np.array([round(cosmo.D_A(z),3) for z in yang['z_c']])
yang['D_A'] = D_A

yang.write('output/Ngal_{}_{}_ra_{}_{}_dec_{}_{}.csv'.format(Ngal_range[0],
    Ngal_range[1], ra_range[0], ra_range[1], dec_range[0], dec_range[1]))
