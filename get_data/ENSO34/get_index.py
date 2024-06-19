#!/usr/bin/env python

# Retrieve an ENSO3.4 index

import os
from urllib.request import urlretrieve

opdir = "%s/indices/ENSO3.4" % os.getenv("SCRATCH")
if not os.path.isdir(opdir):
    os.makedirs(opdir, exist_ok=True)

url = "https://www.psl.noaa.gov/data/correlation/nina34.anom.data"
fname = "%s/%s" % (opdir, "nina34.anom.data")
urlretrieve(url, fname)
