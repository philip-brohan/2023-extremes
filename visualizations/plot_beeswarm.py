#!/usr/bin/env python

# Make monthly global mean time-series (raw anomaly)
# and plot a beeswarm plot.

# Inspired by the FT's version:
# https://x.com/janatausch/status/1798620656525000763

import os
import sys
import iris
import numpy as np
import random
from scipy import stats
import tensorflow as tf
from scipy.interpolate import make_interp_spline

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import matplotlib.gridspec as gridspec

import cmocean

from utilities import grids
from fit_linear.apply_fit import get_residual, get_fit

from makeDataset import getDataset

import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--month", help="Month to show", type=int, required=False, default=None
)
parser.add_argument(
    "--value", help="raw|fit|residual", type=str, required=False, default="raw"
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


# From the python graph gallery (https://python-graph-gallery.com/509-introduction-to-swarm-plot-in-matplotlib/)
def simple_beeswarm(y, nbins=None):

    # Convert y to a NumPy array
    y = np.asarray(y)

    # Calculate the number of bins if not provided
    if nbins is None:
        nbins = len(y) // 6

    # Get upper and lower bounds of the data
    x = np.zeros(len(y))
    ylo = np.min(y)
    yhi = np.max(y)

    # Calculate the size of each bin based on the number of bins
    dy = (yhi - ylo) / nbins

    # Calculate the upper bounds of each bin using linspace
    ybins = np.linspace(ylo + dy, yhi - dy, nbins - 1)

    # Divide the indices into bins
    i = np.arange(len(y))
    ibs = [0] * nbins  # List to store indices for each bin
    ybs = [0] * nbins  # List to store values for each bin
    nmax = 0  # Variable to store the maximum number of data points in a bin
    for j, ybin in enumerate(ybins):

        # Create a boolean mask for elements that are less than or equal to the bin upper bound
        f = y <= ybin

        # Store the indices and values that belong to this bin
        ibs[j], ybs[j] = i[f], y[f]

        # Update nmax with the maximum number of elements in a bin so far
        nmax = max(nmax, len(ibs[j]))

        # Update i and y by excluding the elements already added to the current bin
        f = ~f
        i, y = i[f], y[f]

    # Add the remaining elements to the last bin
    ibs[-1], ybs[-1] = i, y
    nmax = max(nmax, len(ibs[-1]))

    # Assign x indices to the data points in each bin
    dx = 1 / (nmax // 2)

    for i, y in zip(ibs, ybs):
        if len(i) > 1:

            # Determine the index to start from based on whether the bin has an even or odd number of elements
            j = len(i) % 2

            # Sort the indices in the bin based on the corresponding values
            i = i[np.argsort(y)]

            # Separate the indices into two groups, 'a' and 'b'
            a = i[j::2]
            b = i[j + 1 :: 2]

            # Assign x values to the 'a' group using positive values and to the 'b' group using negative values
            x[a] = (0.5 + j / 3 + np.arange(len(b))) * dx
            x[b] = (0.5 + j / 3 + np.arange(len(b))) * -dx

    return x


# Go through data and assemble time-series

trainingData = getDataset(
    startyear=args.startyear,
    endyear=args.endyear,
    cache=False,
    blur=1.0e-9,
).batch(1)
dts = []
members = []
raw = []
residual = []
rawC = grids.HadCRUTCube.copy()
rawC_areas = grids.HadCRUTCube_grid_areas
for batch in trainingData:
    year = int(batch[1].numpy()[0][:4])
    month = int(batch[1].numpy()[0][5:7])
    member = int(batch[1].numpy()[0][8:11])
    if member % 10 <= 5:  # Only plot half the members - less messy
        continue
    if args.month is not None and month != args.month:
        continue
    value = np.squeeze(np.ma.masked_array(batch[0].numpy(), np.isnan(batch[0].numpy())))
    if args.value == "fit":
        rawC.data = value
        rawC = get_fit(rawC, year, month)
        value = rawC.data
    elif args.value == "residual":
        rawC.data = value
        rawC = get_residual(rawC, year, month)
        value = rawC.data
    raw.append(np.ma.average(value, weights=rawC_areas))
    dts.append(year + (month - 0.5) / 12)

# Split off the data for the last 12 months
ltm = sorted(list(set(dts)))[-12:]
raw_ltm = [x for x, y in zip(raw, dts) if y in ltm]
dts_ltm = [x for x in dts if x in ltm]
raw = [x for x, y in zip(raw, dts) if y not in ltm]
dts = [x for x in dts if x not in ltm]

# don't want to plot Jan-Dec in order - show last 12 months
last_month = sorted(list(set(dts_ltm)))[-1]
month_offset = (11.5 / 12) - (last_month % 1)


# Functions to shift data and labels so last month is at the bottom
def shift_month_y(x):
    for i in range(len(x)):
        x[i] += month_offset
        if x[i] > 1:
            x[i] -= 1
    return x


def shift_month_labels(labels):
    x = [0] * len(labels)
    for i in range(len(labels)):
        x[i] = ((i + 0.5) / 12 + month_offset) % 1
    labels = [label for _, label in sorted(zip(x, labels))]
    return labels


# Plot the beeswarm plot
fig = Figure(
    figsize=(9, 10),
    dpi=300,
    facecolor=(0.975, 0.975, 0.975, 1),
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
    "size": 16,
}
matplotlib.rc("font", **font)

# Colour palette for the decades
cmap = matplotlib.colormaps["viridis"]

# 2 subfigures: 1 for the plot, 1 for the legend
gs = gridspec.GridSpec(1, 2, width_ratios=[3, 1])
subfigs = [fig.add_subfigure(spec) for spec in gs]

# Plot
subfigs[0].set_facecolor(fig.get_facecolor())
raw_axes = subfigs[0].subplots(nrows=1, ncols=1, squeeze=True)
raw_axes.set_facecolor((0.85, 0.85, 0.85, 1))
raw_axes.set_xlim(left=args.ymin, right=args.ymax, auto=False)
raw_axes.set_ylim(bottom=1.0, top=0.0, auto=False)
raw_axes.set_yticks(np.linspace(0.5 / 12, 11.5 / 12, 12))
raw_axes.set_yticklabels(
    shift_month_labels(
        [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]
    )
)
raw_axes.grid(color=(0, 0, 0, 1), linestyle="-", linewidth=0.1)
mnth = [x % 1 for x in dts]
decade = [int(x / 10) for x in dts]
for month in list(set(mnth)):
    x = [x for x, m in zip(raw, mnth) if m == month]
    dy = simple_beeswarm(x)
    y = [m for m in mnth if m == month]
    y = shift_month_y(y)
    y = [y[i] + dy[i] / 24 for i in range(len(y))]
    c = [x for x, m in zip(decade, mnth) if m == month]
    raw_axes.scatter(
        x,
        y,
        color=(0, 0, 0, 1),
        s=15,
    )
    raw_axes.scatter(
        x,
        y,
        c=c,
        cmap=cmap,
        s=10,
    )
mnth_ltm = [x % 1 for x in dts_ltm]
line_x = []
line_y = []
for month in list(set(mnth_ltm)):
    x = [x for x, m in zip(raw_ltm, mnth_ltm) if m == month]
    dy = [random.uniform(-1, 1) for _ in range(len(x))]
    y = [m for m in mnth_ltm if m == month]
    y = shift_month_y(y)
    line_y.append(y[0])
    y = [y[i] + dy[i] / 96 for i in range(len(y))]
    raw_axes.scatter(
        x,
        y,
        color=(0, 0, 0, 1),
        s=15,
    )
    raw_axes.scatter(
        x,
        y,
        color=(1, 0, 0, 1),
        s=10,
    )
    line_x.append(np.mean(x))
# Add a nice curve passing through the last 12 month's points
sorted_pairs = sorted(zip(line_y, line_x))
y, x = zip(*sorted_pairs)
spline = make_interp_spline(y, x, k=3)
y = np.linspace(0.01, 0.99, 100)
x = spline(y)
raw_axes.plot(x, y, color=(1, 0, 0, 1), linewidth=1, zorder=35)

# Legend
subfigs[1].set_facecolor(fig.get_facecolor())
legend_axes = subfigs[1].subplots(nrows=1, ncols=1, squeeze=True)
legend_axes.set_facecolor(fig.get_facecolor())
legend_axes.set_axis_off()

legend_elements = [
    Patch(facecolor=cmap((1975 - 1970) / (2024 - 1970)), label="1970s"),
    Patch(facecolor=cmap((1985 - 1970) / (2024 - 1970)), label="1980s"),
    Patch(facecolor=cmap((1995 - 1970) / (2024 - 1970)), label="1990s"),
    Patch(facecolor=cmap((2005 - 1970) / (2024 - 1970)), label="2000s"),
    Patch(facecolor=cmap((2015 - 1970) / (2024 - 1970)), label="2010s"),
    Patch(facecolor=cmap((2022 - 1970) / (2024 - 1970)), label="2020s"),
    Patch(facecolor=(1, 0, 0, 1), label="Last 12 months"),
]

legend = legend_axes.legend(handles=legend_elements, loc="upper right")
legend.get_frame().set_facecolor((0.85, 0.85, 0.85, 1))

fileT = "beeswarm_%s" % args.value
if args.month is not None:
    fileT += "_%02d" % args.month
fig.savefig("%s.webp" % fileT)
