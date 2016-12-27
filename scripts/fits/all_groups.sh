#!/bin/bash

for g in $(ls $LOCAL_DATA/hsc/stamps/candy); do
    python batch_fit.py ${g/group-/}
done
