#!/usr/bin/env python

# Make all the normalization fits

import os

sDir = os.path.dirname(os.path.realpath(__file__))


def is_done(month):
    fn = "%s/Ex-2023/fit_linear/slope_m%02d.nc" % (
        os.getenv("SCRATCH"),
        month,
    )
    if os.path.exists(fn):
        return True
    return False


for month in range(1, 13):
    if is_done(month):
        continue
    cmd = "%s/fit_for_month.py --month=%02d" % (
        sDir,
        month,
    )
    print(cmd)
