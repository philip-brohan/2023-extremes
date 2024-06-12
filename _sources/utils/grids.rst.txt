Define a standard grid 
======================

We're only using HadCRUT data, so we'll use the HadCRUT5 grid as a standard.

This file provides a standard HadCRUT5 grid. The file provides two variables:

* HadCRUTCube - an iris cube on the HadCRUT5 grid (5x5 degree)
* HadCRUTCube_grid_areas - numpy array of grid-cell area weights (for area-weighted averaging)

.. literalinclude:: ../../utilities/grids.py

