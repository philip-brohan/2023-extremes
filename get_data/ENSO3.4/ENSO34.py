# Functions to load The ENSO3.4 index

import os
import sys
import numpy as np

opdir = "%s/indices/ENSO3.4" % os.getenv("SCRATCH")


def load():
    fname = "%s/nina34.anom.data" % opdir
    if not os.path.isfile(fname):
        raise Exception("No data file %s" % fname)

    # Define a validation function
    def valid_line(line):
        try:
            # Try to convert the first value to an integer (the year)
            year = int(line.strip().split()[0])
            return year
        except ValueError:
            # If it fails, this is not a valid data line
            return False

    # Use genfromtxt with the validation function
    data = np.genfromtxt(
        fname, skip_header=1, invalid_raise=False, converters={0: valid_line}
    )

    dts = []
    values = []
    for i in range(data.shape[0]):
        for m in range(1, 13):
            dts.append(int(data[i][0]) + m / 12)
            values.append(data[i][m])
    dts = np.array(dts)
    values = np.array(values)
    dts = dts[values > -99]
    values = values[values > -99]
    return dts, values
