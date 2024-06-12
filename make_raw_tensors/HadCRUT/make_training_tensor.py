#!/usr/bin/env python

# Read in monthly variable from HadCRUT
# Convert into a TensorFlow tensor.
# Serialise and store on $SCRATCH.

# This version keeps original resolution

import os
import sys
import tensorflow as tf
import dask

# Going to do external parallelism - run this on one core
tf.config.threading.set_inter_op_parallelism_threads(1)
dask.config.set(scheduler="single-threaded")

from tensor_utils import load_raw, raw_to_tensor

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--year", help="Year", type=int, required=True)
parser.add_argument("--month", help="Integer month", type=int, required=True)
parser.add_argument("--member", help="Ensemble member", type=int, required=True)
parser.add_argument(
    "--opfile", help="tf data file name", default=None, type=str, required=False
)
args = parser.parse_args()
if args.opfile is None:
    args.opfile = ("%s/EX-2023/raw_datasets/HadCRUT_original_grid/%04d-%02d_%03d.tfd") % (
        os.getenv("SCRATCH"),
        args.year,
        args.month,
        args.member,
    )

if not os.path.isdir(os.path.dirname(args.opfile)):
    os.makedirs(os.path.dirname(args.opfile))

# Load and standardise data
qd = load_raw(args.year, args.month, args.member)
ict = raw_to_tensor(qd)

# Write to file
sict = tf.io.serialize_tensor(ict)
tf.io.write_file(args.opfile, sict)
