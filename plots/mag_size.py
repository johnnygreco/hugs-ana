#!/Users/protostar/anaconda/envs/lsst/bin/python

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import astropy.units as u
from astropy.table import Table
cmap = plt.cm.rainbow
plt.style.use('jpg')

def make_plot(subplots=None):

    if subplots is None:
        fig, a = plt.subplots(figsize=(10,8))
    else:
        fig, a = subplots

    datDIR = os.path.join(os.environ.get('DATA_DIR'), 'gemini_FT_6-2016/')
    vanDokkum = Table.read(datDIR+'vanDokkum2015_Table_1.txt', format='ascii')
    brodie = np.genfromtxt(datDIR+'sizetable.txt', 
                           names=('id', 'host', 'M_V', 'logr', 'ref'), 
                           dtype='S10,S10,f8,f8,S10')
    mask = brodie['ref']!=b'vD+15'
    brodie = brodie[mask]
    coma_dm = 35.05
    mihos_MV = [-15.0, -13.5, -14.9]
    mihos_reff = [9.7, 2.9, 5.5]

    # plot lines of constant effective surface brightness
    reff_kpc = np.linspace(0.001,100,100)
    reff_10pc_as = u.radian.to('arcsec')*1e3*reff_kpc/10.0
    for sb in [24, 25, 26, 27, 28]:
        absmag = sb-2.5*np.log10(2*np.pi*reff_10pc_as**2)
        a.plot(absmag, np.log10(reff_kpc), 'k--', zorder=-200)
    
    # plot van Dokkum and Mihos
    a.scatter(vanDokkum['Mg'], np.log10(vanDokkum['reff']), 
              marker='s', s=45, edgecolors='k', alpha=0.8, color=cmap(0.85), 
              label='van Dokkum et al. 2015')
    a.scatter(mihos_MV, np.log10(mihos_reff), marker='^', s=71, c='c', 
              alpha=0.8, label='Mihos et al. 2015')
    a.scatter(brodie['M_V'], brodie['logr']+np.log10(1e-3), c='gray', 
              alpha=0.4, zorder=-10, label='Brodie et al. 2011')
    a.set_ylim(-1.1, 1.6)
    a.set_xlim(-26,-4)
    a.set_ylabel(r'$\log_{10}(r_\mathrm{eff}\ [\mathrm{kpc}])$')
    a.set_xlabel(r'Absolute Magnitude')
    a.minorticks_on()
    a.invert_xaxis()

    # get text rotation angle 
    # convert from data 
    p1 = a.transData.transform_point((absmag[0], np.log10(reff_kpc)[0])) 
    # to screen coords
    p2 = a.transData.transform_point((absmag[1], np.log10(reff_kpc)[1])) 
    rot = np.degrees(np.arctan2(p2[1]-p1[1], p2[0]-p1[0]))

    # add text to figure
    x, dx, y = -17.6, -1, 1.3
    fs = 15.5
    a.text(-15.2, 1.05, r'28 mag arcsec$^{-2}$',
           rotation=rot, fontsize=fs, va='bottom')
    a.text(x, y, '27',rotation=rot, fontsize=fs, va='bottom')
    a.text(x+dx, y, '26',rotation=rot, fontsize=fs, va='bottom')
    a.text(x+2*dx, y, '25',rotation=rot, fontsize=fs, va='bottom')
    a.text(x+3*dx, y, '24',rotation=rot,fontsize=fs, va='bottom') 

    a.text(-5.8, -.4, r'${\bf dSphs}$', color='gray', fontsize=20)
    a.text(-10.7, .55, r'${\bf UDGs}$', color=cmap(0), fontsize=20)
    a.text(-20.5, 1.05, r'${\bf gEs}$', color='gray', fontsize=20)
    a.text(-18, -.8, r'${\bf cEs}$', color='gray', fontsize=20)
    a.text(-14.1, -0.32, r'${\bf dEs}$', color='gray', fontsize=20)
    a.legend(loc='upper left', fontsize=18, labelspacing=0.7)

    a.tick_params(axis='both', labelsize=18)

    return fig, a

def get_candy(fn, remove_duplicates=True):
    from toolbox.astro import angsep
    from hugs.datasets import yang
    from toolbox.cosmo import Cosmology
    cosmo = Cosmology()

    df = pd.read_csv(fn)
    cut = (df['candy']==1) & (df['ell']<0.6)
    df = df[cut]
    df['D_L'] = cosmo.D_L(df['z'])
    df['Mg'] = df['m_tot(g)'] - 5*np.log10(df['D_L']*1e6) + 5 
    df['Mi'] = df['m_tot(i)'] - 5*np.log10(df['D_L']*1e6) + 5 
    return df

if __name__=='__main__':

    savedir = os.path.join(os.environ.get('FIG_DIR'), 'paper-I')

    path = os.environ.get('HUGS_PIPE_IO')
    fn = os.path.join(path, 'viz-inspect-results/viz-sample.csv')
    fig, ax = make_plot()
    candy = get_candy(fn) 

    ax.scatter(candy['Mg'], np.log10(candy['r_kpc(g)']), s=120, alpha=0.4, 
               edgecolors='k', color=cmap(0), label='HSC UDGs (this work)')

    handles, labels = ax.get_legend_handles_labels()
    handles = [handles[-1]] + handles[:-1]
    labels = [labels[-1]] + labels[:-1]
    ax.legend(handles, labels, loc='upper left', fontsize=18, labelspacing=0.7)

    fig.savefig(os.path.join(savedir, 'size_vs_mag.pdf'))

    try: import RaiseWindow
    except: pass
    plt.show()
