from __future__ import division, print_function

import os
from datetime import datetime
import numpy as np
import pandas as pd

__all_ = ['CatButler', 'merge_synth_cats', 
          'get_group_cats', 'remove_duplicates']


class CatButler(object):

    def __init__(self, path, synths=False):

        self.rundir = path
        self.synths = synths
        label = 'synth-run' if synths else 'batch-run' 
        self.prefix = 'synths' if synths else 'hugs-pipe'

        contents = os.listdir(self.rundir)
        files = [fn for fn in contents if '_z' in fn]

        self._patches = None

    @property
    def patches(self):
        if self._patches is None:
            fn = os.path.join(self.rundir, 'hsc-wide-patches-full.csv')
            self._patches = pd.read_csv(fn)
        return self._patches

    def get_patch_cat(self, tract, patch, kind='candy', fn=None):
        fn = fn if fn else self.prefix+'-cat-'+kind+'.csv'
        path = os.path.join(self.rundir, str(tract)+'/'+patch)            
        patch_fn = os.path.join(path, fn)
        if os.path.isfile(patch_fn):
            df = pd.read_csv(patch_fn)
            df['tract'] = tract
            df['patch'] = patch
        else:
            df = pd.DataFrame({'tract': [tract], 'patch': [patch]})
        if fn=='synths.csv':
            for col in df.columns:
                if col not in ['tract', 'patch', 'synth_id']:
                    df.rename(columns={col: col+'_syn'}, inplace=True)
        return df

    def combine_patch_cats(self, patches=None, **kwargs):
        if patches is None:
            patches = self.patches
        df = []
        for _, row in patches.iterrows():
            tract, patch = row[['tract', 'patch']]
            df.append(self.get_patch_cat(tract, patch, **kwargs))
        df = pd.concat(df, ignore_index=True)
        return df


def remove_duplicates(cat, min_sep=0.7):
    """
    Build mask for double entries in a catalog. 
    Consider object within min_sep arcsec the same object
    """
    from toolbox.astro import angsep
    mask = np.ones(len(cat), dtype=bool)
    cat.reset_index(drop=True, inplace=True)
    counts = []
    for i, (ra, dec) in enumerate(cat[['ra','dec']].values):
        # don't search objects flagged as double entries
        if mask[i]==True:
            seps = angsep(ra, dec, cat['ra'], cat['dec'])
            unique = seps > min_sep
            unique[i] = True # it will certainly match itself
            mask &= unique   # double entries set to False
    cat.drop(cat.index[~mask], inplace=True)


def merge_synth_cats(observed, model):
    merged = pd.merge(observed,
                      model,
                      on=['tract', 'patch', 'synth_id'],
                      how='inner', 
                      suffixes=['_obs', '_syn'])
    return merged
