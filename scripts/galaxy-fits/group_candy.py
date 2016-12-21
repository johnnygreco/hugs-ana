#!/Users/protostar/anaconda/envs/lsst/bin/python

import os
import hugs

group_id = 9552

rundir = 'hsc/stamps/temp_candy/group-'+str(group_id)
rundir = os.path.join(os.environ.get('LOCAL_DATA'), rundir)

hugs.tasks.fit_candy_stamps(rundir)
