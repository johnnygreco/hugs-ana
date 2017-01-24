from __future__ import division, print_function

from .. import hugged

def test_CatButler():

    cb = hugged.CatButler()

    assert type(cb.z_max)==float
    assert type(cb.logMh_lims[0])==float

    group_id = 9552 
    cat = cb.get_group_cat(group_id)
    npatch = len(cat[['tract', 'patch']].drop_duplicates())

    assert len(cb.patches_dict[group_id])==npatch

def test_merge_synth_cats():

    cb = hugged.CatButler(synths=True)

    syn = cb.get_group_cat(9552, fn='synths.csv')
    cat = cb.get_group_cat(9552)

    merged = hugged.merge_synth_cats(cat, syn)
    nsyn_found = (cat['synth_id']>-1).sum()

    assert len(merged)==nsyn_found
