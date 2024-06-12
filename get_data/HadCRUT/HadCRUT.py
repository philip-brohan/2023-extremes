# Functions to load HadCRUT

import os
import iris
import iris.coord_systems

# Specify a coordinate system to add on load so the cubes work properly with iris.
CMS = iris.coord_systems.RotatedGeogCS(90, 180, 0)

version = "5.0.2.0"
opdir = "%s/HadCRUT/%s" % (os.getenv("SCRATCH"), version)

# Only using a subset of the members
members = [
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    151,
    152,
    153,
    154,
    155,
    156,
    157,
    158,
    159,
    160,
]


# And a function to add the coord system to a cube (in-place)
def add_coord_system(cbe):
    cbe.coord("latitude").coord_system = CMS
    cbe.coord("longitude").coord_system = CMS


def load(year=None, month=None, member=None, grid=None):
    if year is None or month is None or member is None:
        raise Exception("Year, month and member must be specified")
    fname = "%s/HadCRUT.%s.analysis.anomalies.%d.nc" % (opdir, version, member)
    if not os.path.isfile(fname):
        raise Exception("No data file %s" % fname)
    ftt = iris.Constraint(
        time=lambda cell: cell.point.month == month and cell.point.year == year
    )
    varC = iris.load_cube(fname, ftt)
    add_coord_system(varC)
    if grid is not None:
        varC.coords("latitude")[0].bounds = None
        varC.coords("longitude")[0].bounds = None
        varC = varC.regrid(grid, iris.analysis.Linear())
    return varC
