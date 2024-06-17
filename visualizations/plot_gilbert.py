#!/usr/bin/env python

# Plot the gilbert 1d values

import os
import sys
import numpy as np

from utilities import plots, grids

from utilities.gilbert_xy2d import gilbert_xy2d

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

import cmocean

# Make a cube of gilbert data
gbt = grids.HadCRUTCube.copy()
for i in range(36):
    for j in range(72):
        gbt.data[i, j] = gilbert_xy2d(i, j, 36, 72) / (36 * 72)


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
    gbt,
    vMin=0,
    vMax=1,
    cMap=matplotlib.colormaps["viridis"],
)

fig.savefig("gilbert.webp")
