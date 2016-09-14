
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import matplotlib.pyplot as plt
from toolbox.image import zscale
from toolbox.utils.plotting import ticks_off
plt.style.use('jpg')

def overlay_mask(img, mask, cmap=plt.cm.gray_r, contrast=0.25, 
                 subplots=None, figsize=(8,6)):
    if subplots is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig, ax = subplots
    vmin, vmax = zscale(img, contrast=contrast)
    ax.imshow(img, vmin=vmin, vmax=vmax, origin='lower', cmap=cmap)
    mask = mask.astype(float)
    mask[mask==0.0] = np.nan
    ax.imshow(mask, origin='lower', alpha=0.4, 
              vmin=0, vmax=1, cmap='rainbow_r')
    ticks_off(ax)
    try: import RaiseWindow
    except: pass
    plt.show()
