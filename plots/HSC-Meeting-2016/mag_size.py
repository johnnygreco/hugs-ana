#!/usr/bin/env python 

import os
import numpy as np
import matplotlib.pyplot as plt
from astropy.table import Table, vstack
import astropy.units as u
import hugs
from toolbox.cosmo import Cosmology
cosmo = Cosmology()
cmap = plt.cm.rainbow
plt.style.use('jpg')
saveDIR = os.path.join(os.environ.get('DROP_DIR'), 'talks/hsc-meeting-2016-talk/')

# get data
g_i = 0.8
datDIR = os.path.join(os.environ.get('DATA_DIR'), 'gemini_FT_6-2016/')
vanDokkum = Table.read(datDIR+'vanDokkum2015_Table_1.txt', format='ascii')
brodie = np.genfromtxt(datDIR+'sizetable.txt', names=('id', 'host', 'M_V', 'logr', 'ref'), dtype='S10,S10,f8,f8,S10')
mask = brodie['ref']!=b'vD+15'
brodie = brodie[mask]
coma_dm = 35.05
mihos_MV = [-15.0, -13.5, -14.9]
mihos_reff = [9.7, 2.9, 5.5]

fig, a = plt.subplots(figsize=(10,8))

# plot lines of constant effective surface brightness
reff_kpc = np.linspace(0.001,100,100)
reff_10pc_as = u.radian.to('arcsec')*1e3*reff_kpc/10.0
for sb in [24, 25, 26, 27, 28]:
    absmag = sb-2.5*np.log10(2*np.pi*reff_10pc_as**2)
    a.plot(absmag, np.log10(reff_kpc), 'k--', zorder=-200)
    
# plot van Dokkum and Mihos
a.scatter(vanDokkum['Mg']-g_i, np.log10(vanDokkum['reff']), marker='s', s=45, edgecolors='k',
          alpha=0.8, color=cmap(0.85), label='van Dokkum et al. 2015')
a.scatter(mihos_MV, np.log10(mihos_reff), marker='^', s=71, c='c', alpha=0.8, label='Mihos et al. 2015')
a.scatter(brodie['M_V'], brodie['logr']+np.log10(1e-3), c='gray', alpha=0.4,
          zorder=-10, label='Brodie et al. 2011')
a.set_ylim(-1, 1.6)
a.set_xlim(-25,-5)
a.set_ylabel(r'$\log_{10}(r_\mathrm{eff}\ [\mathrm{kpc}])$')
a.set_xlabel(r'Absolute Magnitude')
a.minorticks_on()
a.invert_xaxis()

# get text rotation angle 
p1 = a.transData.transform_point((absmag[0], np.log10(reff_kpc)[0])) # convert from data 
p2 = a.transData.transform_point((absmag[1], np.log10(reff_kpc)[1])) # to screen coords
rot = np.degrees(np.arctan2(p2[1]-p1[1], p2[0]-p1[0]))

# add text to figure
x, dx, y = -17.6, -1, 1.3
fs = 15.5
a.text(-15.2, 1.05, r'28 mag arcsec$^{-2}$',rotation=rot, fontsize=fs, va='bottom')
a.text(x, y, '27',rotation=rot, fontsize=fs, va='bottom')
a.text(x+dx, y, '26',rotation=rot, fontsize=fs, va='bottom')
a.text(x+2*dx, y, '25',rotation=rot, fontsize=fs, va='bottom')
a.text(x+3*dx, y, '24',rotation=rot,fontsize=fs, va='bottom') 

a.text(-5.8, -.4, r'${\bf dSphs}$', color='gray', fontsize=20)
a.text(-10.3, .4, r'${\bf UDGs}$', color=cmap(0.85), fontsize=20)
a.text(-20.5, 1.05, r'${\bf gEs}$', color='gray', fontsize=20)
a.text(-18, -.8, r'${\bf cEs}$', color='gray', fontsize=20)
a.text(-14.1, -0.32, r'${\bf dEs}$', color='gray', fontsize=20)
a.legend(loc='upper left', fontsize=18, labelspacing=0.7)
fig.savefig(saveDIR+'/mag_vs_size_no_hsc.pdf')

# plot my candidates
group_info = hugs.datasets.load_yang_groups()
results_dir = '../../results/'
files = [results_dir+f for f in os.listdir(results_dir) if 'group' in f if 'rand' not in f]
cands = Table()
for fn in files:
    tab = Table.read(fn+'/viz_cat.txt', format='ascii')
    group_id = fn.split('_')[-1]
    z = group_info['z'][int(group_id)-1]
    D_L, D_A = cosmo.D_L(z), cosmo.D_A(z)
    r_eff = tab['FLUX_RADIUS']*hugs.pixscale*u.arcsecond.to('radian')*D_A*1e3
    Mi = tab['MAG_AUTO'] - 5*np.log10(D_L*1e6) + 5
    tab['r_eff']  = r_eff 
    tab['Mi']  = Mi
    cands = vstack([cands, tab])
mask = hugs.doubles_mask(cands)
cands = cands[mask]
print(len(cands))
a.scatter(cands['Mi'], np.log10(cands['r_eff']), s=120, alpha=0.6, edgecolors='k', 
          color=cmap(0), label='HSC UDGs (9 groups)')
a.legend(loc='upper left', fontsize=18, labelspacing=0.7)
fig.savefig(saveDIR+'/mag_vs_size_with_hsc.pdf')
fig.savefig(saveDIR+'/mag_vs_size.eps')

try: import RaiseWindow
except: pass
plt.show()
