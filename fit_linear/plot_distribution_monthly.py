#!/usr/bin/env python

# Plot raw and residual anomalies for a selected month
# Map and distribution.

import os
import sys
import numpy as np

from utilities import plots, grids
from get_data.HadCRUT import HadCRUT

from normalize import load_fitted, normalize_cube

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

import cmocean
import argparse

from scipy.stats import gamma

parser = argparse.ArgumentParser()
parser.add_argument(
    "--year", help="Year to plot", type=int, required=False, default=1969
)
parser.add_argument(
    "--month", help="Month to plot", type=int, required=False, default=3
)

parser.add_argument(
    "--member",
    help="Ensemble member to use. (Default, sample randomly)",
    type=int,
    default=1,
)
args = parser.parse_args()

# Load the fitted values
(slope, intercept, variance) = load_fitted(args.month)

# Load the raw data for the selected month
raw = HadCRUT.load(
    year=args.year,
    month=args.month,
    member=args.member,
    grid=grids.HadCRUTCube,
)

# Make the normalized version
residual = normalize_cube(raw, args.year, args.month, slope, intercept, variance)

# Make the plot
fig = Figure(
    figsize=(10 * 3 / 2, 10),
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

# choose actual and normalized data colour maps
cmaps = (cmocean.cm.balance, cmocean.cm.balance)

ax_raw = fig.add_axes([0.02, 0.515, 0.607, 0.455])
vMin = np.percentile(raw.data.compressed(), 1)
plots.plotFieldAxes(
    ax_raw,
    raw,
    vMin=-7,
    vMax=7,
    cMap=cmaps[0],
)

ax_hist_raw = fig.add_axes([0.683, 0.535, 0.303, 0.435])
plots.plotHistAxes(ax_hist_raw, raw, vMin=-7, vMax=7, bins=25)

ax_normalized = fig.add_axes([0.02, 0.03, 0.607, 0.455])
plots.plotFieldAxes(
    ax_normalized,
    residual,
    vMin=-5,
    vMax=5,
    cMap=cmaps[1],
)

ax_hist_normalized = fig.add_axes([0.683, 0.05, 0.303, 0.435])
plots.plotHistAxes(ax_hist_normalized, residual, vMin=-5, vMax=5, bins=25)


fig.savefig("monthly.webp")
