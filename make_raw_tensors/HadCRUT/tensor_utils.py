# Utility functions for creating and manipulating raw tensors

import numpy as np
import tensorflow as tf

from get_data.HadCRUT import HadCRUT
from utilities import grids

rng = np.random.default_rng()


# Load the data for 1 month (on the standard cube)
def load_raw(year, month, member=None):
    if member is None:
        member = HadCRUT.members[rng.integers(low=0, high=len(HadCRUT.members), size=1)]
    raw = HadCRUT.load(
        year=year,
        month=month,
        member=member,
        grid=grids.HadCRUTCube,
    )
    if np.ma.is_masked(raw.data):
        raw.data.data[raw.data.mask == True] = np.nan
    return raw


# Convert raw cube to tensor
def raw_to_tensor(raw):
    ict = tf.convert_to_tensor(raw.data, tf.float32)
    return ict


# Convert tensor to cube
def tensor_to_cube(tensor):
    cube = grids.E5sCube.copy()
    cube.data = tensor.numpy()
    cube.data = np.ma.MaskedArray(cube.data, np.isnan(cube.data))
    return cube
