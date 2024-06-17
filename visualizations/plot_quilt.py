#!/usr/bin/env python

# Make monthly gridded time-series (raw anomalies)
# and plot the 2d grid (time v location)

import os
import sys
import iris
import numpy as np
import pickle
from scipy import stats
import tensorflow as tf

from utilities.gilbert_xy2d import gilbert_xy2d
from utilities import grids

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D

import cmocean

from get_data.HadCRUT.HadCRUT import members
from fit_linear.apply_fit import get_residual, get_fit

from makeDataset import getDataset

import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--month", help="Month to show", type=int, required=False, default=None
)
parser.add_argument(
    "--vmin", help="Range minimum", type=float, required=False, default=None
)
parser.add_argument(
    "--vmax", help="Range maximum", type=float, required=False, default=None
)
parser.add_argument(
    "--value", help="raw|fit|residual", type=str, required=False, default="raw"
)
parser.add_argument(
    "--startyear", help="Start Year", type=int, required=False, default=1970
)
parser.add_argument(
    "--endyear", help="End Year", type=int, required=False, default=2025
)

args = parser.parse_args()

# Make a Hilbert-curve index to map 2d->1d preserving location
gbt = np.zeros((36, 72))
for i in range(36):
    for j in range(72):
        gbt[i, j] = gilbert_xy2d(i, j, 36, 72)
gbt = gbt.flatten()
gbt_inv = np.argsort(gbt)

# Go through data and assemble time-series

trainingData = getDataset(
    startyear=args.startyear,
    endyear=args.endyear,
    cache=False,
    blur=1.0e-9,
).batch(1)

if args.month is None:
    dts = list(range(args.startyear * 12, args.endyear * 12))
else:
    dts = list(range(args.startyear, args.endyear))
raw = np.zeros((36 * 72, len(dts)))
rawC = grids.HadCRUTCube.copy()

min_dts = 9999
max_dts = 0
for batch in trainingData:
    year = int(batch[1].numpy()[0][:4])
    month = int(batch[1].numpy()[0][5:7])
    member = int(batch[1].numpy()[0][8:11])
    if args.month is not None and month != args.month:
        continue
    if args.month is None:
        dtsc = year * 12 + (month - 1) - args.startyear * 12
    else:
        dtsc = year - args.startyear
    memc = members.index(member)
    value = np.squeeze(np.ma.masked_array(batch[0].numpy(), np.isnan(batch[0].numpy())))
    if args.value == "fit":
        rawC.data = value
        rawC = get_fit(rawC, year, month)
        value = rawC.data
    elif args.value == "residual":
        rawC.data = value
        rawC = get_residual(rawC, year, month)
        value = rawC.data
    raw[:, dtsc] += value.flatten()[gbt_inv]
    min_dts = min(min_dts, dtsc)
    max_dts = max(max_dts, dtsc)

raw /= len(members)
raw[:, :min_dts] = np.nan
raw[:, max_dts:] = np.nan

# Plot the quilt
fig = Figure(
    figsize=(10, 10),
    dpi=100,
    facecolor=(0.95, 0.95, 0.95, 1),
    edgecolor=None,
    linewidth=0.0,
    frameon=True,
    subplotpars=None,
    tight_layout=None,
)
canvas = FigureCanvas(fig)
font = {
    "family": "sans-serif",
    "sans-serif": "Arial",
    "weight": "normal",
    "size": 12,
}
matplotlib.rc("font", **font)

# Single plot - anomaly quilt
raw_axes = fig.subplots(nrows=1, ncols=1, squeeze=True)
fig.subplots_adjust(left=0.025, right=0.95, bottom=0.075, top=0.95)
raw_axes.set_facecolor((0.75, 0.75, 0.75, 1))
if args.month is None:
    dts = [i / 12 for i in dts]
raw_axes.set_xlim(left=min(dts), right=max(dts), auto=False)
raw_axes.set_ylim(bottom=0, top=raw.shape[1], auto=False)
raw_axes.set_yticks([])
raw_axes.set_title("HadCRUT %s" % args.value)
raw_axes.set_xlabel("Year")
raw_axes.grid(color=(0, 0, 0, 1), linestyle="-", linewidth=0.1)

cmap = cmocean.cm.balance

# plot the quilt as an image
quilt = raw_axes.imshow(
    raw,
    aspect="auto",
    cmap=cmap,
    origin="upper",
    extent=[min(dts), max(dts), 0, raw.shape[1]],
    vmin=args.vmin,
    vmax=args.vmax,
    zorder=10,
)

# Add a colorbar to the right
cbar = fig.colorbar(
    quilt,
    #    matplotlib.cm.ScalarMappable(cmap=cmap),
    ax=raw_axes,
    orientation="vertical",
    fraction=0.02,
    pad=0.02,
)

fileT = "plot_quilt_%s" % args.value
if args.month is not None:
    fileT += "_%02d" % args.month
fig.savefig("%s.webp" % fileT)
