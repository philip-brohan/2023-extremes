# Provide a function to apply the pre-calculated linear model
import numpy as np

import os
import iris

from fit_linear.normalize import normalize_cube, unnormalize_cube, load_fitted

# Load the pre-calculated fitted values
fitted = {"slope": [None] * 13, "intercept": [None] * 13, "variance": [None] * 13}

for month in range(1, 13):
    fitted["slope"][month], fitted["intercept"][month], fitted["variance"][month] = (
        load_fitted(month)
    )


def get_residual(cube, year, month):
    residual = normalize_cube(
        cube,
        year,
        month,
        fitted["slope"][month],
        fitted["intercept"][month],
        fitted["variance"][month],
    )
    return residual


def get_fit(cube, year, month):
    fit = cube.copy()
    fit.data = fitted["slope"][month].data * year + fitted["intercept"][month].data
    return fit
