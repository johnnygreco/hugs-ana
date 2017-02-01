from __future__ import division, print_function

import os
from datetime import datetime
import numpy as np
import pandas as pd
hugs_pipe_io = os.environ.get('HUGS_PIPE_IO')

__all_ = ['CatButler', 'merge_synth_cats', 
          'get_group_cats', 'remove_duplicates']


def _find_most_recent(path=hugs_pipe_io, label='batch-run'):
    dirs = [d for d in os.listdir(path) if label in d]
    time_fmt = '%Y%m%d-%H%M%S'
    dirs.sort(key=lambda d: datetime.strptime(d[len(label)+1:], time_fmt))
    return os.path.join(path, dirs[-1])


class CatButler(object):

    def __init__(self, rundir=None, synths=False):

        self.synths = synths
        label = 'synth-run' if synths else 'batch-run' 
        self.rundir = rundir if rundir else _find_most_recent(label=label)
        self.prefix = 'synths' if synths else 'hugs-pipe'

        contents = os.listdir(self.rundir)
        files = [fn for fn in contents if '_z' in fn]

        self.labels = files[0].split('_')[1:3]
        self.z_max = float(self.labels[0][1:])
        self.logMh_lims = [float(m) for m in self.labels[1][2:].split('-')]
        
        self._patches_dict = None
        self._group_props = None
        self._unique_patches = None

    @property
    def patches_dict(self):
        if self._patches_dict is None:
            fn = 'cat_{}_{}_tracts_n_patches.npy'.format(*self.labels)
            fn = os.path.join(self.rundir, fn)
            self._patches_dict = np.load(fn).item()
        return self._patches_dict

    @property
    def group_props(self):
        if self._group_props is None:
            fn = 'cat_{}_{}_group_info.csv'.format(*self.labels)
            fn = os.path.join(self.rundir, fn)
            self._group_props = pd.read_csv(fn)
        return self._group_props

    @property
    def unique_patches(self):
        if self._unique_patches is None:
            fn = 'patches_{}_{}.csv'.format(*self.labels)
            fn = os.path.join(self.rundir, fn)
            self._unique_patches =  pd.read_csv(fn)
        return self._unique_patches

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
            df.rename(columns={'patch_id': 'synth_id'}, inplace=True)
            df.rename(columns={'mu0_'+b: 'mu_0('+b+')' for b in 'gri' }, 
                      inplace=True)
            df.rename(columns={'mtot_'+b: 'm_tot('+b+')' for b in 'gri' }, 
                      inplace=True)
            for col in df.columns:
                if col not in ['tract', 'patch', 'synth_id']:
                    df.rename(columns={col: col+'_syn'}, inplace=True)
        return df

    def get_group_cat(self, group_id, **kwargs):
        df = []
        for tract, patch in self.patches_dict[group_id]:
            group_df = self.get_patch_cat(tract, patch, **kwargs)
            group_df['group_id'] = group_id
            df.append(group_df)
        df = pd.concat(df, ignore_index=True)
        return df

    def combine_group_cats(self, groups=None, **kwargs):
        if groups is None:
            groups = self.group_props.group_id.values
        df = []
        for g in groups:
            df.append(self.get_group_cat(g, **kwargs))
        df = pd.concat(df, ignore_index=True)
        return df

    def combine_patch_cats(self, patches=None, **kwargs):
        if patches is None:
            patches = self.unique_patches
        df = []
        for _, row in patches.iterrows():
            tract, patch = row[['tract', 'patch']]
            df.append(self.get_patch_cat(tract, patch, **kwargs))
        df = pd.concat(df, ignore_index=True)
        return df


def remove_duplicates(cat, min_sep=0.7, group_ids=None):
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
            if group_ids is not None:
                counts.append(cat.loc[~unique, group_ids].sum(axis=0).values)
        else:
            if group_ids is not None:
                counts.append(np.zeros(len(group_ids)))
    if group_ids is not None:
        counts = pd.DataFrame(columns=group_ids, data=counts, dtype=int)
        cat.loc[:, group_ids] = cat.loc[:, group_ids].copy() + counts
    cat.drop(cat.index[~mask], inplace=True)


def merge_synth_cats(observed, model):
    merged = pd.merge(observed,
                      model,
                      on=['tract', 'patch', 'synth_id'],
                      how='inner', 
                      suffixes=['_obs', '_syn'])
    return merged
