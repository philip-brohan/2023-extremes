#!/usr/bin/env python

# Investigate regridding weirdness

import os
import iris
import iris.time
import numpy as np

from utilities import plots, grids
from HadCRUT import load

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

import cmocean
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--month", help="Month to plot", type=int, required=False, default=3
)
parser.add_argument(
    "--year", help="Year to plot", type=int, required=False, default=1969
)
parser.add_argument(
    "--member", help="Member to plot", type=int, required=False, default=1
)
args = parser.parse_args()

ogrid = load(args.year, args.month, args.member)
rgrid = load(args.year, args.month, args.member, grid=grids.E5sCube)

# Make the plot
fig = Figure(
    figsize=(10, 10),
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

ax_o = fig.add_axes([0.05, 0.03, 0.9, 0.45])
plots.plotFieldAxes(
    ax_o,
    ogrid,
    vMin=np.percentile(np.ma.compressed(ogrid.data), 1),
    vMax=np.percentile(np.ma.compressed(ogrid.data), 99),
    cMap=cmocean.cm.balance,
)

ax_r = fig.add_axes([0.05, 0.515, 0.9, 0.45])
plots.plotFieldAxes(
    ax_r,
    rgrid,
    vMin=np.percentile(np.ma.compressed(rgrid.data), 1),
    vMax=np.percentile(np.ma.compressed(rgrid.data), 99),
    cMap=cmocean.cm.balance,
)


fig.savefig("rg_tst.png")
