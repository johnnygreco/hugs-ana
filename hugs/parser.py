
__all__ = ['parse_args']

def parse_args(relpath=False, HSC_info=False):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('tract', type=str, help='HSC tract')
    parser.add_argument('patch', type=str, help='HSC patch')
    parser.add_argument('-b', '--band', help='HSC band', default='I')
    args = parser.parse_args()
    band, tract, patch = args.band.upper(), args.tract, args.patch
    if relpath:
        return 'HSC-'+band+'/'+str(tract)+'/'+patch[0]+'-'+patch[-1]
    elif HSC_info:
        return band, tract, patch
    else:
        return args
