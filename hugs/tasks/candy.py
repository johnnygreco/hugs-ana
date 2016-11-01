from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import numpy as np
import matplotlib.pyplot as plt
from astropy.table import Table, vstack, hstack

from .fit_gal import fit_gal
from .. import utils
from ..datasets import hsc
from .. import imfit
STAMPDIR = os.path.join(utils.hugs_pipe_io, 'stamps')

__all__ = ['get_candy_stamps', 'fit_candy_stamps']


def get_candy_stamps(cat, label=None, bands='GRI', outdir=STAMPDIR):
    """
    Get postage stamps from database. 

    Parameters
    ----------
    cat : astropy.table.Table
        Source catalog (output from hugs_pipe).
    label : string, optional
        Label for stamps. If None, will use time.
    bands : string or list, optional
        Photometric bands to get. 
    outdir : string, optional
        Output directory.
    """
    
    if label is None:
        import time
        label = time.strftime("%Y%m%d-%H%M%S")
        rundir = os.path.join(outdir, 'stamps_'+label)
    else:
        rundir = os.path.join(outdir, label)
    utils.mkdir_if_needed(rundir)

    new_cat_fn = os.path.join(rundir, 'candy.cat')
    cat.write(new_cat_fn, format='ascii')

    coordlist_fn = os.path.join(rundir, 'coordlist.txt')
    hsc.make_query_coordlist(cat, coordlist_fn, bands)
    hsc.cutout_query(coordlist_fn, outdir=rundir)

    # give stamps more useful names
    stamp_files = [f for f in os.listdir(rundir) if f[-4:]=='fits']
    stamp_files = sorted(stamp_files, key=lambda f: int(f.split('-')[0]))
    grouped_files = utils.grouper(stamp_files, len(bands))

    for num, files in enumerate(grouped_files):
        for i in range(len(bands)):
            old_fn = files[i]
            rerun = old_fn.split('-')[-1]
            rerun = rerun.replace('_', '-')
            new_fn = 'candy-{}-{}-{}'.format(num, bands[i].lower(), rerun)
            old_fn = os.path.join(rundir, old_fn)
            new_fn = os.path.join(rundir, new_fn)
            os.rename(old_fn, new_fn)


def fit_candy_stamps(label, cat=None, bands='GRI', save_figs=True):
    """
    Fit Seric models to postage-stamp candidate images.
    
    Parameters
    ----------
    label : string
        Label for all files/candidates in this run.
    cat : astropy.table.Table, optional
        hugs-pipe catalog of candidates. If None, must exist
        within the "rundir".
    bands : string or list, optional
        Photometric bands to be fit. 
    save_figs : bool
        If True, save a summary figure for each candidate.

    Notes
    -----
    All bands are fit separately. Then, the band with the smallest
    fractional error in r_eff is used as a reference for forced 
    photometry on the other bands, where the position and sercic
    index is held fixed. 
    """

    rundir = os.path.join(STAMPDIR, label)

    # if directory does not exist, get the stamps 
    if not os.path.isdir(rundir):
        assert cat is not None
        get_candy_stamps(cat, label=label, bands=bands)
    else:
        cat_fn = os.path.join(rundir, 'candy.cat')
        cat = Table.read(cat_fn, format='ascii')

    # get stamp files and group by candidates
    stamp_files = [f for f in os.listdir(rundir) if 
                   f.split('-')[-1]=='wide.fits']
    stamp_files = sorted(stamp_files, key=lambda f: int(f.split('-')[1]))
    stamp_files = utils.grouper(stamp_files, len(bands))

    # all imfit results will be saved in imfit directory
    imfitdir = os.path.join(rundir, 'imfit')
    utils.mkdir_if_needed(imfitdir)

    # loop over candidates 
    candy_params = Table()
    for candy_files in stamp_files:	
        candy_nums = np.array([int(f.split('-')[1]) for f in candy_files])
        assert np.alltrue(candy_nums==candy_nums[0])
        num = candy_nums[0]

        if save_figs:
            fig, axes = plt.subplots(len(bands), 3, figsize=(15,15))
            fig.subplots_adjust(wspace=0.05, hspace=0.05)

        # get initial guess parameters
        pa = cat['orientation'][num] * 180.0/np.pi
        pa = 90 + pa 
        ell = cat['ellipticity'][num]
        init_params = {'PA': [pa, 0, 180],
                       'ell': [ell, 0, 0.999]}
        ra, dec = cat['ra', 'dec'][num]
        
        # fit all bands separately
        r_e_err = []
        fits = []
        mask_files = [] 
        for fn in candy_files:
            band = fn.split('-')[2]
            fn = os.path.join(rundir, fn)
            prefix = os.path.join(imfitdir, 'candy-{}-{}'.format(num, band))
            sersic = fit_gal(fn, 
                             prefix=prefix,
                             init_params=init_params,
                             visualize=False, 
                             band=band, 
                             clean='config')
            r_e_err.append(sersic.r_e_err/sersic.r_e)
            fits.append(sersic)
            mask_files.append(prefix+'_photo_mask.fits')
        r_e_err = np.array(r_e_err)
        best_idx = r_e_err.argmin()
        best_band = candy_files[best_idx].split('-')[2]

        # generate ouput columns for best band
        best = fits[best_idx]
        data = [num, best_band, ra, dec, best.n, best.m_tot, best.mu_0, 
                best.ell, best.r_e*utils.pixscale, best.PA]
        names = ['candy_num', 
                 'best_band',
                 'ra',
                 'dec',
                 'n', 
                 'm_tot('+best_band+')', 
                 'mu_0('+best_band+')',
                 'ell('+best_band+')',
                 'r_e('+best_band+')', 
                 'PA('+best_band+')']
        temp_best = Table(rows=[data], names=names)
        
        if save_figs:
            imfit.viz.img_mod_res(os.path.join(rundir, candy_files[best_idx]), 
                                  fits[best_idx].params, 
                                  mask_files[best_idx], 
                                  band=best_band,
                                  subplots=(fig, axes[0]),
                                  show=False)
        
        # perform forced photometry with "best" band as the reference
        ax_count = 1
        for idx, fn in enumerate(candy_files):
            if idx!=best_idx:
                band = fn.split('-')[2]
                fn = os.path.join(rundir, fn)
                init_params = {'X0': [fits[best_idx].X0, 'fixed'],
                               'Y0': [fits[best_idx].Y0, 'fixed'],
                               'n': [fits[best_idx].n, 'fixed'],
                               'r_e': fits[best_idx].r_e,
                               'I_e': fits[idx].I_e,
                               'PA': [fits[idx].PA, 0, 180], 
                               'ell': [ell, 0, 0.999]}
                prefix = 'candy-{}-{}-forced-{}'.format(num, band, best_band)
                prefix = os.path.join(imfitdir, prefix)
                sersic = fit_gal(fn, 
                                 prefix=prefix,
                                 init_params=init_params,
                                 visualize=False, 
                                 clean='config',
                                 band=band,
                                 photo_mask_fn=mask_files[best_idx])

                # generate output columns for other bands
                data = [sersic.m_tot, sersic.mu_0, sersic.ell,
                        sersic.r_e*utils.pixscale, sersic.PA]
                names = ['m_tot('+band+')', 'mu_0('+band+')', 'ell('+band+')',
                         'r_e('+band+')', 'PA('+band+')']
                temp_other = Table(rows=[data], names=names)
                temp_best = hstack([temp_best, temp_other])

                if save_figs:
                    imfit.viz.img_mod_res(fn, 
                                          sersic.params, 
                                          mask_files[best_idx], 
                                          band=band,
                                          subplots=(fig, axes[ax_count]),
                                          show=False, 
                                          titles=False)
                    ax_count += 1

        for mask_fn in mask_files:
            os.remove(mask_fn)

        if save_figs:
            fig_fn = 'candy-{}-fit-results.pdf'.format(num)
            fig_fn = os.path.join(imfitdir, fig_fn)
            fig.savefig(fig_fn)
            fig.clf()

        candy_params = vstack([candy_params, temp_best])

    out_fn = os.path.join(imfitdir, 'candy-imfit-params.cat')
    candy_params.write(out_fn, format='ascii')
