from __future__ import division, print_function 

from . import datasets
from .utils import *
from . import imtools

try:
    from . import imfit
    from . import tasks
except ImportError:
    warn = ('Warning: must have lsst stack ' 
           'installed to use the imfit and task modules')
    print(warn)
