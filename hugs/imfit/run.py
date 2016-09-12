from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


def run(fn, x0, y0, mask=None, var=None, config='default', 
        saveconfig=False):
    import subprocess
    if (mask is None) and (var is None):
        cmd = 'imfit '+fn
    subprocess.call(shell=True)
