from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import numpy as np

__all__ = ['io', 'pixscale', 'bit_dict', 'bit_flag_dict', 
	   'get_arg_parser', 'mkdir_if_needed', 'grouper']
           

io = os.environ.get('HUGS_PIPE_IO')
pixscale = 0.168 # arcsec/pixel

bit_dict =  {1: 'BAD',                
             2: 'SATURATED',          
             4: 'INTERPOLATED',       
             8: 'CR',                 
             16: 'EDGE',              
             32: 'DETECTED',          
             64: 'DETECTED_NEGATIVE', 
             128: 'SUSPECT',          
             256: 'NO_DATA',          
             512: 'BRIGHT_OBJECT',    
             1024: 'CLIPPED',         
             2048: 'CROSSTALK',       
             4096: 'NOT_DEBLENDED',   
             8192: 'UNMASKEDNAN'}     

bit_flag_dict = dict((v,k) for k,v in bit_dict.items())


def get_arg_parser(description='hugs parser'):
    from argparse import ArgumentParser
    parser = ArgumentParser(description)
    parser.add_argument('tract', type=int, help='HSC tract')
    parser.add_argument('patch', type=str, help='HSC patch')
    parser.add_argument('-b', '--band', help='HSC band', default='I')
    return parser


def mkdir_if_needed(directory):
    """"
    Create directory if it does not exist.
    """
    if not os.path.isdir(directory):
        os.mkdir(directory)


def grouper(iterable, n, fillvalue=None):
    """
    Group iterable into n groups.
    """
    from six.moves import zip_longest
    grouped_iterable = zip_longest(*[iter(iterable)]*n, fillvalue=fillvalue)
    return list(grouped_iterable)
