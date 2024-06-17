#!/usr/bin/env python

# Fit a linear model at each month and grid point

import os
import sys
import iris
import numpy as np
import pickle
from scipy import stats
import tensorflow as tf

from utilities import grids
from get_data.HadCRUT.HadCRUT import members

from makeDataset import getDataset

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--month", help="Month to fit", type=int, required=True)

parser.add_argument(
    "--startyear", help="Start Year", type=int, required=False, default=1970
)
parser.add_argument(
    "--endyear", help="End Year", type=int, required=False, default=2020
)

parser.add_argument(
    "--opdir",
    help="Directory for output files",
    default="%s/Ex-2023/fit_linear" % os.getenv("SCRATCH"),
)
args = parser.parse_args()
opdir = args.opdir
if not os.path.isdir(opdir):
    os.makedirs(opdir, exist_ok=True)


# Go through data and assemble time-series for each point
trainingData = getDataset(
    startyear=args.startyear,
    endyear=args.endyear,
    cache=False,
    blur=1.0e-9,
).batch(1)
nFields = (args.endyear - args.startyear + 1) * len(members)
dts = np.full((nFields), np.nan)
values = np.full((36, 72, nFields), np.nan)
means = np.full((nFields), np.nan)
count = 0
for batch in trainingData:
    year = int(batch[1].numpy()[0][:4])
    month = int(batch[1].numpy()[0][5:7])
    if month == args.month:
        values[:, :, count] = np.squeeze(batch[0].numpy())
        means[count] = np.nanmean(values[:, :, count])
        dts[count] = year + (month - 0.5) / 12
        count += 1

# Fit the linear model at each grid-point
slope = np.full((36, 72), np.nan)
intercept = np.full((36, 72), np.nan)
variance = np.full((36, 72), np.nan)
for i in range(36):
    for j in range(72):
        x = dts[~np.isnan(values[i, j, :])]
        y = values[i, j, ~np.isnan(values[i, j, :])]
        if len(x) < 10:
            continue
        try:
            slope[i, j], intercept[i, j], r_value, p_value, std_err = stats.linregress(
                x, y
            )
        except:
            continue
        predicted = slope[i, j] * x + intercept[i, j]
        residuals = y - predicted
        variance[i, j] = np.nanvar(residuals)

# Same fit for the global means
x = dts[~np.isnan(means)]
y = means[~np.isnan(means)]
mfit = stats.linregress(x, y)
predicted = mfit.slope * x + mfit.intercept
residuals = y - predicted
varianceM = np.nanvar(residuals)

# Save the fit parameters
slopeC = grids.HadCRUTCube.copy()
slopeC.data = slope
slopeC.data = np.ma.MaskedArray(slopeC.data, np.isnan(slopeC.data))
slopeC.data.data[slopeC.data.mask] = 1.0
iris.save(
    slopeC,
    "%s/slope_m%02d.nc" % (args.opdir, args.month),
)
interceptC = grids.HadCRUTCube.copy()
interceptC.data = intercept
interceptC.data = np.ma.MaskedArray(interceptC.data, np.isnan(interceptC.data))
interceptC.data.data[interceptC.data.mask] = 1.0
iris.save(
    interceptC,
    "%s/intercept_m%02d.nc" % (args.opdir, args.month),
)
varianceC = grids.HadCRUTCube.copy()
varianceC.data = variance
varianceC.data = np.ma.MaskedArray(varianceC.data, np.isnan(varianceC.data))
varianceC.data.data[varianceC.data.mask] = 1.0
iris.save(
    varianceC,
    "%s/variance_m%02d.nc" % (args.opdir, args.month),
)

with open("%s/means_m%02d.pkl" % (args.opdir, args.month), "wb") as pkf:
    pickle.dump((mfit.slope, mfit.intercept, varianceM), pkf)
