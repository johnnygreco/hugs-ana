"""
Collection of visualization functions for imfit. 
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import matplotlib.pyplot as plt

__all__ = ['imfit_results']

def imfit_results(img, mod, res):
    """
    Show imfit results: image, model, and 
    residuals.
    """
