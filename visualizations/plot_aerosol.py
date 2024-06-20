#!/usr/bin/env python

# Plot map of Masaru's aerosol data

import os
import sys
import iris
import numpy as np

from utilities import grids, plots

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D

import cmocean

from Masaru_data.Masaru import load_aerosol


import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--vmin", help="Range minimum", type=float, required=False, default=None
)
parser.add_argument(
    "--vmax", help="Range maximum", type=float, required=False, default=None
)
parser.add_argument(
    "--type", help="ship100|ship20", type=str, required=True, default=None
)
parser.add_argument("--fig", help="1|2|4", type=int, required=True, default=None)
parser.add_argument(
    "--log", help="Take log of input?", action="store_true", default=False
)
parser.add_argument(
    "--landmask", help="Mask out land data?", action="store_true", default=False
)
parser.add_argument(
    "--no-regrid", help="Regrid to HadCRUT?", action="store_true", default=False
)

args = parser.parse_args()


# Load the data

lgrid = None
if not args.no_regrid:
    lgrid = grids.HadCRUTCube
raw = load_aerosol(fig=args.fig, type=args.type, grid=lgrid, landmask=args.landmask)
if args.log:
    raw.data = np.log10(raw.data)

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
plots.plotFieldAxes(
    ax_raw,
    raw,
    vMin=args.vmin,
    vMax=args.vmax,
    cMap=cmocean.cm.balance,
)

fileT = "aerosol_fig%d_%s" % (
    args.fig,
    args.type,
)
fig.savefig("%s.webp" % fileT)
