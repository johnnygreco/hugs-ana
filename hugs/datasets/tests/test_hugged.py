from __future__ import division, print_function

from .. import hugged

def test_HugsCat():

    hc = hugged.HugsCat()

    assert type(hc.z_max)==float
    assert type(hc.logMh_lims[0])==float

    group_id = 9552 
    cat = hc.get_group_cat(group_id)
    npatch = len(cat[['tract', 'patch']].drop_duplicates())

    assert len(hc.patches_dict[group_id])==npatch

def test_merge_synth_cats():

    hc = hugged.HugsCat(synths=True)

    syn = hc.get_group_cat(9552, fn='synths.csv')
    cat = hc.get_group_cat(9552)

    merged = hugged.merge_synth_cats(cat, syn)
    nsyn_found = (cat['synth_id']>-1).sum()

    assert len(merged)==nsyn_found
