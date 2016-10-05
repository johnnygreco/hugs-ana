#!/Users/protostar/anaconda/envs/lsst/bin/python

import os
import hugs

#dataID = {'tract': 9348, 'patch': '7,6', 'filter': 'HSC-I'}
#dataID = {'tract': 9617, 'patch': '8,3', 'filter': 'HSC-I'}
dataID = {'tract': 9589, 'patch': '3,0', 'filter': 'HSC-I'}
displays = hugs.pipe.run(dataID)
