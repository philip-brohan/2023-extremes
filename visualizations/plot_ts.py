#!/usr/bin/env python

# Make monthly global mean time-series (raw anomalies)
# and plot them.

import os
import sys
import iris
import numpy as np
import pickle
from scipy import stats
import tensorflow as tf

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D

import cmocean

from utilities import grids
from fit_linear.apply_fit import get_residual, get_fit
from fit_enso.apply_fit import get_enso_residual, get_enso_fit

from makeDataset import getDataset

import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--month", help="Month to show", type=int, required=False, default=None
)
parser.add_argument(
    "--value",
    help="raw|fit|residual|fit_enso|residual_enso",
    type=str,
    required=False,
    default="raw",
)
parser.add_argument(
    "--startyear", help="Start Year", type=int, required=False, default=1970
)
parser.add_argument(
    "--endyear", help="End Year", type=int, required=False, default=2050
)
parser.add_argument(
    "--ymin", help="Min of y-axis", type=float, required=False, default=-0.5
)
parser.add_argument(
    "--ymax", help="Max of y-axis", type=float, required=False, default=1.5
)


args = parser.parse_args()

# Go through data and assemble time-series

trainingData = getDataset(
    startyear=args.startyear,
    endyear=args.endyear,
    cache=False,
    blur=1.0e-9,
).batch(1)
dts = []
raw = []
members = []
rawC = grids.HadCRUTCube.copy()
rawC_areas = grids.HadCRUTCube_grid_areas
for batch in trainingData:
    year = int(batch[1].numpy()[0][:4])
    month = int(batch[1].numpy()[0][5:7])
    member = int(batch[1].numpy()[0][8:11])
    if args.month is not None and month != args.month:
        continue
    value = np.squeeze(np.ma.masked_array(batch[0].numpy(), np.isnan(batch[0].numpy())))
    if args.value == "fit":
        rawC.data = value
        rawC = get_fit(rawC, year, month)
        value = rawC.data
    elif (
        args.value == "residual"
        or args.value == "enso_fit"
        or args.value == "enso_residual"
    ):
        rawC.data = value
        rawC = get_residual(rawC, year, month)
        value = rawC.data
        if args.value == "enso_fit":
            rawC = get_enso_fit(rawC, year, month)
            value = rawC.data
        if args.value == "enso_residual":
            rawC = get_enso_residual(rawC, year, month)
            value = rawC.data
    raw.append(np.ma.average(value, weights=rawC_areas))
    dts.append(year + (month - 0.5) / 12)
    members.append(member)

# Plot the time-series
fig = Figure(
    figsize=(15, 5),
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

# Single plot - raw anomalies
raw_axes = fig.subplots(nrows=1, ncols=1, squeeze=True)
raw_axes.set_facecolor((0.95, 0.95, 0.95, 1))
raw_axes.set_xlim(left=min(dts), right=max(dts), auto=False)
raw_axes.set_ylim(bottom=args.ymin, top=args.ymax, auto=False)
raw_axes.set_ylabel("HadCRUT %s" % args.value)
raw_axes.set_xlabel("Year")
raw_axes.grid(color=(0, 0, 0, 1), linestyle="-", linewidth=0.1)
member_list = list(set(members))
for m in range(len(member_list)):
    raw_axes.add_line(
        Line2D(
            [dts[i] for i in range(len(dts)) if members[i] == member_list[m]],
            [raw[i] for i in range(len(dts)) if members[i] == member_list[m]],
            linewidth=2,
            color=(0, 0, 1, 1),
            alpha=0.05,
            zorder=20,
        )
    )

fileT = "plot_ts_%s" % args.value
if args.month is not None:
    fileT += "_%02d" % args.month
fig.savefig("%s.webp" % fileT)
