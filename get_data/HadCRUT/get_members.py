#!/usr/bin/env python

# Retrieve HadCRUT5

import os
from urllib.request import urlretrieve
import zipfile

# When this changes, probably check the HadCRUT web site for other changes
version = "5.0.2.0"

opdir = "%s/HadCRUT/%s" % (os.getenv("SCRATCH"), version)
if not os.path.isdir(opdir):
    os.makedirs(opdir, exist_ok=True)

for members in ("1_to_10", "151_to_160"):
    url = (
        "https://www.metoffice.gov.uk/hadobs/hadcrut5/data/HadCRUT.%s/"
        +"analysis/HadCRUT.%s.analysis.anomalies.%s_netcdf.zip"
    ) % (version, version,members)
    fname = "%s/%s.zip" % (opdir, members)
    urlretrieve(url, fname)
    with zipfile.ZipFile(fname, "r") as zip_ref:
        zip_ref.extractall(opdir)
    os.remove(fname)
