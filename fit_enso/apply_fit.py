# Provide a function to apply the pre-calculated linear model
import numpy as np

import os
import iris

from fit_enso.normalize import normalize_cube, load_fitted

# Load the pre-calculated fitted values
fitted = {"slope": None, "intercept": None, "variance": None}
fitted["slope"], fitted["intercept"], fitted["variance"] = load_fitted()

# Load the ENSO indices
from get_data.ENSO34 import ENSO34

ENSO = {}
ENSO["dts"], ENSO["values"] = ENSO34.load()


def get_enso_index(year, month):
    index = ENSO["values"][ENSO["dts"] == "%04d-%02d" % (year, month)][0]
    return index


def get_enso_residual(cube, year, month):
    residual = normalize_cube(
        cube,
        get_enso_index(year, month),
        fitted["slope"],
        fitted["intercept"],
        fitted["variance"],
    )
    return residual


def get_enso_fit(cube, year, month):
    fit = cube.copy()
    fit.data = (
        fitted["slope"].data * get_enso_index(year, month) + fitted["intercept"].data
    )
    return fit
