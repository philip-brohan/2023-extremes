# Apply the pre-calculated linear model and calculate residuals
import numpy as np

import os
import iris

iris.FUTURE.datum_support = True  # Don't care, and gets rid of the error message


# Load the pre-calculated fitted values
def load_fitted(month):
    slope = iris.load_cube(
        "%s/Ex-2023/fit_linear/slope_m%02d.nc" % (os.getenv("SCRATCH"), month),
    )
    intercept = iris.load_cube(
        "%s/Ex-2023/fit_linear/intercept_m%02d.nc" % (os.getenv("SCRATCH"), month),
    )
    variance = iris.load_cube(
        "%s/Ex-2023/fit_linear/variance_m%02d.nc" % (os.getenv("SCRATCH"), month),
    )
    return (slope, intercept, variance)


# Normalise a cube (subtract linear fit and divide residual by sd)
def normalize_cube(raw, year, month, slope, intercept, variance):
    x = year + (month - 0.5) / 12
    fit = slope.data * x + intercept.data
    residual = raw.copy()
    residual.data = (raw.data - fit) / np.sqrt(variance.data)
    return residual


# Convert a cube from normalized value to raw
def unnormalize_cube(residual, year, month, slope, intercept, variance):
    x = year + (month - 0.5) / 12
    fit = slope.data * x + intercept.data
    raw = residual.copy()
    raw.data = (residual.data * np.sqrt(variance.data)) + fit
    return raw
