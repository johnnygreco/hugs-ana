#!/usr/bin/env python 

from __future__ import division, print_function 

import numpy as np

import sexpy
import hugs
from hugs import imtools

def run_pipe(relpath):
    for step, config in hugs.pipe_steps:
        check_imgs = config.pop('set_check_images', None)
        sw = sexpy.SexWrapper(config)
        if check_imgs is not None:
            sw.set_check_images(check_imgs[0], prefix=check_imgs[1])
        print(step)
        print(sw.get_config())

if __name__=='__main__':
    relpath = hugs.parser.parse_args(relpath=True)
    run_pipe(relpath)
