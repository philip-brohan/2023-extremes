# Functions to load Masaru's aerosol and forcing data

import os
import iris
import iris.cube
import iris.util
import iris.coord_systems
import numpy as np

from utilities.plots import get_land_mask

iris.FUTURE.datum_support = True  # Don't care, and gets rid of the error message

# Specify a coordinate system to add on load so the cubes work properly with iris.
CMS = iris.coord_systems.RotatedGeogCS(90, 180, 0)


root_dir = os.path.abspath(os.path.dirname(__file__))


# And a function to add the coord system to a cube (in-place)
def add_coord_system(cbe):
    cbe.coord("latitude").coord_system = CMS
    cbe.coord("longitude").coord_system = CMS


def load_aerosol(fig=1, type="ship100", grid=None, landmask=False):
    if fig == 1:
        if type == "ship100":
            fname = (
                "%s/data4PhilipBrohan/fig1/SO2_all_low_anthropogenic_ECLIPSE_V6b_CLE_base_ship100all_2014_2101_time_series_n96.nc"
                % root_dir
            )
        elif type == "ship20":
            fname = (
                "%s/data4PhilipBrohan/fig1/SO2_all_low_anthropogenic_ECLIPSE_V6b_CLE_base_ship20all_2014_2101_time_series_n96.nc"
                % root_dir
            )
        elif type == "diff":
            fname = (
                "%s/data4PhilipBrohan/fig1/diff_SO2_all_low_anthropogenic_ECLIPSE_V6b_CLE_base_ship20all-ship100all_2014_2101_time_series_n96.nc"
                % root_dir
            )
        else:
            raise Exception("Unknown aerosol type %s" % type)
        if not os.path.isfile(fname):
            raise Exception("No data file %s" % fname)
        varC = iris.load_cube(
            fname, iris.Constraint(time=lambda cell: cell.point.year <= 2024)
        )
        varC = varC.collapsed("time", iris.analysis.MEAN)

    if fig == 2:
        files = os.listdir("%s/data4PhilipBrohan/fig2/%s" % (root_dir, type))
        varC = None
        for file in files:
            cTmp = iris.load_cube(
                "%s/data4PhilipBrohan/fig2/%s/%s" % (root_dir, type, file)
            )
            if varC is None:
                varC = cTmp
            else:
                varC.data += cTmp.data
        varC.data /= len(files)

    varC = iris.util.squeeze(varC)  # Remove unnecessary height dimension
    add_coord_system(varC)
    if grid is not None:
        varC = varC.regrid(grid, iris.analysis.Linear())
    if landmask:
        lm = get_land_mask()
        lm = lm.regrid(varC, iris.analysis.Linear())
        varC.data = np.ma.masked_where(lm.data > 0.5, varC.data)
    return varC
