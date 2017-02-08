#!/Users/protostar/anaconda/envs/lsst/bin/python

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import lsst.afw.image as afwImage
import lsst.afw.display as afwDisp
import lsst.afw.geom as afwGeom
import lsst.afw.display.rgb as afwRgb

def postage_stamp(path, candy_num, show=True, save_fn=None):
    files = [fn for fn in os.listdir(path) if 'wide.fits' in fn]
    candy_files = [fn for fn in files if '-'+str(candy_num)+'-' in fn]
    images = {}
    for fn in candy_files:
        band = fn.split('-')[2].lower()
        fn = os.path.join(path, fn)
        images.update({band: afwImage.ImageF(fn)})

    kws = {'Q': 10, 'dataRange': 0.5}
    rgb_img = afwRgb.makeRGB(images['i'], 
                             images['r'], 
                             images['g'], 
                             **kws)
    fig, ax = plt.subplots(figsize=(8,8), 
                           subplot_kw={'xticks':[], 'yticks':[]})
    ax.imshow(rgb_img, origin='lower')
    if show:
        plt.show()
    if save_fn:
        fig.savefig(save_fn, bbox_inches='tight')
    plt.close() 

if __name__=='__main__':
    path = os.environ.get('LOCAL_DATA')
    path = os.path.join(path, 'hsc/stamps/candy/20170130-143629')
    cat = pd.read_csv(os.path.join(path, 'candy.csv'))

    udg_like = [0, 102, 103, 104, 109, 115, 25,
                120, 126, 134, 140, 162, 190, 28]
    for num in udg_like:
        print num
        mu0 = cat.loc[num, ['mu_0(g)']].values[0]
        save_fn = '/Users/protostar/Desktop/hugs-images/udg-like/'
        save_fn = save_fn+'num-{}-mu0g-{:0.1f}.pdf'.format(num, mu0)
        postage_stamp(path, num, show=False, save_fn=save_fn)

    lumpy = [13, 145, 151, 16, 165, 170, 196, 199, 209, 62, 72,
             171, 172, 177, 179, 184, 185, 187, 188, 3, 38, 99, 125]
    for num in lumpy:
        print num
        mu0 = cat.loc[num, ['mu_0(g)']].values[0]
        save_fn = '/Users/protostar/Desktop/hugs-images/lumpy-ish/'
        save_fn = save_fn+'num-{}-mu0g-{:0.1f}.pdf'.format(num, mu0)
        postage_stamp(path, num, show=False, save_fn=save_fn)

    nearby = [24, 26, 27, 31]
    for num in nearby:
        print num
        mu0 = cat.loc[num, ['mu_0(g)']].values[0]
        save_fn = '/Users/protostar/Desktop/hugs-images/likely-nearby/'
        save_fn = save_fn+'num-{}-mu0g-{:0.1f}.pdf'.format(num, mu0)
        postage_stamp(path, num, show=False, save_fn=save_fn)

    tidal = [214, 112, 50, 63, 97, 142]
    for num in tidal:
        print num
        mu0 = cat.loc[num, ['mu_0(g)']].values[0]
        save_fn = '/Users/protostar/Desktop/hugs-images/maybe-tidal/'
        save_fn = save_fn+'num-{}-mu0g-{:0.1f}.pdf'.format(num, mu0)
        postage_stamp(path, num, show=False, save_fn=save_fn)
