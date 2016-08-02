
__all__ = ['parse_args']

def parse_args(relpath=False):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('tract', type=str, help='HSC tract')
    parser.add_argument('patch', type=str, help='HSC patch')
    parser.add_argument('-b', '--band', help='HSC band', default='I')
    args = parser.parse_args()
    if relpath:
        tract, patch, band = args.tract, args.patch, args.band.upper()
        return 'HSC-'+band+'/'+str(tract)+'/'+patch[0]+'-'+patch[-1]
    else:
        return args
