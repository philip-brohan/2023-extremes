#!/usr/bin/env python

# Fit a linear model to ENSO3.4 at each grid point

import os
import sys
import iris
import numpy as np
from scipy import stats
import tensorflow as tf

from utilities import grids
from fit_linear.apply_fit import get_residual
from get_data.HadCRUT.HadCRUT import members

from fit_linear.makeDataset import getDataset
from get_data.ENSO34 import ENSO34

import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--startyear", help="Start Year", type=int, required=False, default=1970
)
parser.add_argument(
    "--endyear", help="End Year", type=int, required=False, default=2020
)

parser.add_argument(
    "--opdir",
    help="Directory for output files",
    default="%s/Ex-2023/fit_enso" % os.getenv("SCRATCH"),
)
args = parser.parse_args()
opdir = args.opdir
if not os.path.isdir(opdir):
    os.makedirs(opdir, exist_ok=True)

# Get the ENSO time-series
ENSO = {}
ENSO["dts"], ENSO["values"] = ENSO34.load()
# Convery ENSO dates to match internal use
years = np.array([int(d[:4]) for d in ENSO["dts"]])
months = np.array([int(d[5:7]) for d in ENSO["dts"]])
ENSO["dts"] = years * 12 + (months - 1) - args.startyear * 12

rawC = grids.HadCRUTCube.copy()
# Go through data and assemble time-series for each point
#  taking residuals for the linear time model
trainingData = getDataset(
    startyear=args.startyear,
    endyear=args.endyear,
    cache=False,
    blur=1.0e-9,
).batch(1)
nFields = (args.endyear - args.startyear + 1) * 12
dts = np.full((nFields), np.nan)
values = np.full((36, 72, nFields), 0.0)
for batch in trainingData:
    year = int(batch[1].numpy()[0][:4])
    month = int(batch[1].numpy()[0][5:7])
    dtsc = year * 12 + (month - 1) - args.startyear * 12
    value = np.squeeze(np.ma.masked_array(batch[0].numpy(), np.isnan(batch[0].numpy())))
    rawC.data = value
    rawC = get_residual(rawC, year, month)
    value = rawC.data
    values[:, :, dtsc] += value
    dts[dtsc] = dtsc

dts = dts[~np.isnan(dts)]
values = values[:, :, ~np.isnan(dts)]
values /= len(members)

# Match-up the ENSO and HadCRUT time-series
dts_common = np.in1d(dts, ENSO["dts"])
dts = dts[dts_common]
values = values[:, :, dts_common]
dts_common = np.in1d(ENSO["dts"], dts)
ENSO["values"] = ENSO["values"][dts_common]
ENSO["dts"] = ENSO["dts"][dts_common]

# Fit the linear model at each grid-point

slope = np.full((36, 72), np.nan)
intercept = np.full((36, 72), np.nan)
variance = np.full((36, 72), np.nan)
for i in range(36):
    for j in range(72):
        x = ENSO["values"][~np.isnan(values[i, j, :])]
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


# Save the fit parameters
slopeC = grids.HadCRUTCube.copy()
slopeC.data = slope
slopeC.data = np.ma.MaskedArray(slopeC.data, np.isnan(slopeC.data))
slopeC.data.data[slopeC.data.mask] = 1.0
iris.save(
    slopeC,
    "%s/slope.nc" % args.opdir,
)
interceptC = grids.HadCRUTCube.copy()
interceptC.data = intercept
interceptC.data = np.ma.MaskedArray(interceptC.data, np.isnan(interceptC.data))
interceptC.data.data[interceptC.data.mask] = 1.0
iris.save(
    interceptC,
    "%s/intercept.nc" % args.opdir,
)
varianceC = grids.HadCRUTCube.copy()
varianceC.data = variance
varianceC.data = np.ma.MaskedArray(varianceC.data, np.isnan(varianceC.data))
varianceC.data.data[varianceC.data.mask] = 1.0
iris.save(
    varianceC,
    "%s/variance.nc" % args.opdir,
)
