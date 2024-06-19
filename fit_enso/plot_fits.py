#!/usr/bin/env python

# Plot maps of the three parameters in the enso fit
# intercept, slope, and residual variance.

import os
import iris
import iris.time
import numpy as np

from utilities import plots

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

import cmocean
import argparse


# Load the fitted values
slope = iris.load_cube(
    "%s/Ex-2023/fit_enso/slope.nc" % os.getenv("SCRATCH"),
)
intercept = iris.load_cube(
    "%s/Ex-2023/fit_enso/intercept.nc" % os.getenv("SCRATCH"),
)
variance = iris.load_cube(
    "%s/Ex-2023/fit_enso/variance.nc" % os.getenv("SCRATCH"),
)

# Make the plot
fig = Figure(
    figsize=(10, 10 * 3 / 2),
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


ax_intercept = fig.add_axes([0.02, 0.68, 0.8, 0.31])
intercept_img = plots.plotFieldAxes(
    ax_intercept,
    intercept,
    cMap=cmocean.cm.balance,
)
ax_intercept_cb = fig.add_axes([0.85, 0.68, 0.13, 0.31])
ax_intercept_cb.set_axis_off()
cb = fig.colorbar(
    intercept_img,
    ax=ax_intercept_cb,
    location="right",
    orientation="vertical",
    fraction=1.0,
)

ax_slope = fig.add_axes([0.02, 0.345, 0.8, 0.31])
slope_img = plots.plotFieldAxes(
    ax_slope,
    slope,
    cMap=cmocean.cm.balance,
)
ax_slope_cb = fig.add_axes([0.85, 0.345, 0.13, 0.31])
ax_slope_cb.set_axis_off()
cb = fig.colorbar(
    slope_img, ax=ax_slope_cb, location="right", orientation="vertical", fraction=1.0
)

ax_variance = fig.add_axes([0.02, 0.01, 0.8, 0.31])
variance_img = plots.plotFieldAxes(
    ax_variance,
    variance,
    cMap=cmocean.cm.balance,
)
ax_variance_cb = fig.add_axes([0.85, 0.01, 0.13, 0.31])
ax_variance_cb.set_axis_off()
cb = fig.colorbar(
    variance_img,
    ax=ax_variance_cb,
    location="right",
    orientation="vertical",
    fraction=1.0,
)

fig.savefig("fits.webp")
