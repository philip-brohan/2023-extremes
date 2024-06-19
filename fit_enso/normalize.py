# Apply the pre-calculated enso model and calculate residuals
# fits to residuals from the linear time model

import numpy as np

import os
import iris

iris.FUTURE.datum_support = True  # Don't care, and gets rid of the error message


# Load the pre-calculated fitted values
def load_fitted():
    slope = iris.load_cube(
        "%s/Ex-2023/fit_enso/slope.nc" % os.getenv("SCRATCH"),
    )
    intercept = iris.load_cube(
        "%s/Ex-2023/fit_enso/intercept.nc" % os.getenv("SCRATCH"),
    )
    variance = iris.load_cube(
        "%s/Ex-2023/fit_enso/variance.nc" % os.getenv("SCRATCH"),
    )
    return (slope, intercept, variance)


# Normalise a cube (subtract linear fit and divide residual by sd)
def normalize_cube(raw, enso, slope, intercept, variance):
    x = enso
    fit = slope.data * x + intercept.data
    residual = raw.copy()
    residual.data = raw.data - fit  # / np.sqrt(variance.data)
    return residual


# Convert a cube from normalized value to raw
def unnormalize_cube(residual, enso, slope, intercept, variance):
    x = enso
    fit = slope.data * x + intercept.data
    raw = residual.copy()
    raw.data = (residual.data * np.sqrt(variance.data)) + fit
    return raw
