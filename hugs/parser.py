
__all__ = ['parse_args']

def parse_args(kind='pipeline'):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('tract', type=str, help='HSC tract')
    parser.add_argument('patch', type=str, help='HSC patch')
    parser.add_argument('-b', '--band', help='HSC band', default='I')
    parser.add_argument('--text_param', help='ds9 reg text parameter',
                        default='MAG_AUTO')
    args = parser.parse_args()
    band, tract, patch = args.band.upper(), args.tract, args.patch
    if kind=='pipeline':
        return band, tract, patch, args
    elif kind=='relpath':
        return 'HSC-'+band+'/'+str(tract)+'/'+patch[0]+'-'+patch[-1]
    elif kind=='HSC info':
        return band, tract, patch
    else:
        return args
