from __future__ import division, print_function

import os
from datetime import datetime
import numpy as np
import pandas as pd
hugs_pipe_io = os.environ.get('HUGS_PIPE_IO')

__all_ = ['CatButler', 'merge_synth_cats']


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

    def get_group_cat(self, group_id, kind='candy', fn=None):

        fn = fn if fn else self.prefix+'-cat-'+kind+'.csv'

        df = []
        for tract, patch in self.patches_dict[group_id]:
            path = os.path.join(self.rundir, str(tract)+'/'+patch)            
            patch_fn = os.path.join(path, fn)
            if os.path.isfile(patch_fn):
                patch_df = pd.read_csv(patch_fn)
            else:
                patch_df = pd.DataFrame()
            patch_df['tract'] = tract
            patch_df['patch'] = patch 
            df.append(patch_df)
        df = pd.concat(df, ignore_index=True)

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


def merge_synth_cats(observed, model):
    merged = pd.merge(observed,
                      model,
                      on=['tract', 'patch', 'synth_id'],
                      how='inner', 
                      suffixes=['_obs', '_syn'])
    return merged
