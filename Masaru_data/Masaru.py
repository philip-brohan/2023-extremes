# Functions to load Masaru's aerosol and forcing data

import os
import iris
import iris.util
import iris.coord_systems

iris.FUTURE.datum_support = True  # Don't care, and gets rid of the error message

# Specify a coordinate system to add on load so the cubes work properly with iris.
CMS = iris.coord_systems.RotatedGeogCS(90, 180, 0)


root_dir = os.path.abspath(os.path.dirname(__file__))


# And a function to add the coord system to a cube (in-place)
def add_coord_system(cbe):
    cbe.coord("latitude").coord_system = CMS
    cbe.coord("longitude").coord_system = CMS


def load_aerosol(type="ship100", grid=None):
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
    varC = iris.util.squeeze(varC)  # Remove unnecessary height dimension
    add_coord_system(varC)
    if grid is not None:
        #    varC.coords("latitude")[0].bounds = None
        #    varC.coords("longitude")[0].bounds = None
        varC = varC.regrid(grid, iris.analysis.Linear())
    return varC
