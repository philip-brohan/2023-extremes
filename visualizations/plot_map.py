#!/usr/bin/env python

# Plot map of (average of) monthly cvalues

import os
import sys
import iris
import numpy as np
import pickle
from scipy import stats
import tensorflow as tf

from utilities import grids, plots

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
    "--startmonth", help="Start month", type=int, required=True, default=None
)
parser.add_argument(
    "--endmonth", help="End month", type=int, required=True, default=None
)
parser.add_argument(
    "--vmin", help="Range minimum", type=float, required=False, default=-3
)
parser.add_argument(
    "--vmax", help="Range maximum", type=float, required=False, default=3
)
parser.add_argument(
    "--value", help="raw|fit|residual", type=str, required=False, default="raw"
)
parser.add_argument(
    "--startyear", help="Start Year", type=int, required=True, default=None
)
parser.add_argument("--endyear", help="End Year", type=int, required=True, default=None)

args = parser.parse_args()


# Go through data and assemble average over selected months

trainingData = getDataset(
    startyear=args.startyear,
    endyear=args.endyear,
    cache=False,
    blur=1.0e-9,
).batch(1)

raw = np.zeros((36, 72))
rawC = grids.HadCRUTCube.copy()

count = 0
for batch in trainingData:
    year = int(batch[1].numpy()[0][:4])
    month = int(batch[1].numpy()[0][5:7])
    member = int(batch[1].numpy()[0][8:11])
    if not (
        (year > args.startyear or (year == args.startyear and month >= args.startmonth))
        and (year < args.endyear or (year == args.endyear and month <= args.endmonth))
    ):
        continue
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
    raw += value
    count += 1

raw /= count

# Plot the map
# Make the plot
fig = Figure(
    figsize=(10, 5),
    dpi=100,
    facecolor=(0.5, 0.5, 0.5, 1),
    edgecolor=None,
    linewidth=0.0,
    frameon=False,
    subplotpars=None,
    tight_layout=None,
)
canvas = FigureCanvas(fig)
font = {
    "family": "sans-serif",
    "sans-serif": "Arial",
    "weight": "normal",
    "size": 20,
}
matplotlib.rc("font", **font)
axb = fig.add_axes([0, 0, 1, 1])
axb.set_axis_off()
axb.add_patch(
    Rectangle(
        (0, 0),
        1,
        1,
        facecolor=(1.0, 1.0, 1.0, 1),
        fill=True,
        zorder=1,
    )
)

ax_raw = fig.add_axes([0, 0, 1, 1])
rawC.data = raw
plots.plotFieldAxes(
    ax_raw,
    rawC,
    vMin=args.vmin,
    vMax=args.vmax,
    cMap=cmocean.cm.balance,
)

fileT = "plot_map_%s_%04d-%02d_%04d-%02d" % (
    args.value,
    args.startyear,
    args.startmonth,
    args.endyear,
    args.endmonth,
)
fig.savefig("%s.webp" % fileT)
