#!/usr/bin/env python 

from __future__ import print_function

import os
import numpy as np
from astropy.table import Table
import astropy.units as u

from hugs import yang_r180 as r180
from toolbox.cosmo import Cosmology
cosmo = Cosmology()
catdir = os.path.join(os.environ.get('DATA_DIR'), 'catalogs/Yang')
h = cosmo.h

def print_info(ids):

    fn = os.path.join(catdir, 'yang_modelC_all.txt')
    group_members = Table.read(fn, format='ascii')
    fn = os.path.join(catdir, 'group_DR7/modelC_group')
    group = np.loadtxt(fn, skiprows=3, usecols=(0,1,2,3,6,7))
    group = Table([group[:,i] for i in range(group.shape[1])], 
                   names=('group_id', 'ra', 'dec', 'z', 'Mh_Lest', 'Mh_Mest'),
                   dtype=(int, 'f8', 'f8', 'f8', 'f8', 'f8'))

    for group_id in ids:
        # group parameters (luminosity weighted ra, dec, z and angular diameter distance)
        ra, dec, z, Mh_L, Mh_M = group['ra', 'dec', 'z', 'Mh_Lest', 'Mh_Mest'][group_id-1]
        D_A, D_L = cosmo.D_A(z), cosmo.D_L(z)

        # group member positions
        idx = np.argwhere(group_members['group_id']==group_id).T[0]
        positions = group_members['ra', 'dec'][idx]
        Ngal = group_members['Ngal'][idx][0]
        r_180 = r180(10**Mh_L, z)

        print('    group', group_id, 'parameters\n-----------------------------')
        print('ra dec = {} {}\nz = {:.5f}\nD_A = {:.3f} Mpc\nD_L = {:.3f} Mpc\
               \n1\'\'= {:.3f} kpc\nNgal = {}\nMh_Lest = {}\nMh_Mest = {}\nr_180 = {} Mpc'.\
               format(ra,dec,z,D_A,D_L,u.arcsec.to('radian')*D_A*1e3,Ngal,Mh_L,Mh_M,r_180))
        print('   galaxy member positions\n-----------------------------')
        print(positions)
        print()

if __name__=='__main__':
    import sys
    if not len(sys.argv)>1:
        print('usage:', sys.argv[0], 'group1 group2 ...')
        exit(1)
    numgroups = len(sys.argv)-1
    ids = [int(g) for g in sys.argv[1:]]
    print_info(ids)
