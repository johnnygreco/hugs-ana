
__all__ = ['read_cat']

def read_cat(catfile):
    """
    Read SExtractor output catalog using astropy.

    Parameters
    ----------
    catfile : string
      SExtractor output catalog.

    Returns
    -------
    cat : astropy table
      Output sextractor catalog.
    """
    from astropy.table import Table
    from collections import OrderedDict
    cat = Table.read(catfile, format='ascii.sextractor')
    cat.meta = OrderedDict() # bug in astropy sextractor table
    return cat
