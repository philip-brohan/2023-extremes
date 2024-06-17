#!/usr/bin/bash

# Make all the Ex-2023 figures

./plot_ts.py --value=raw
./plot_ts.py --value=raw --month=9
./plot_ts.py --value=fit
./plot_ts.py --value=residual --ymin=-0.55 --ymax=0.75
./plot_ts.py --value=residual --ymin=-0.55 --ymax=0.75 --month=9

./plot_beeswarm.py --value=raw
./plot_beeswarm.py --value=fit
./plot_beeswarm.py --value=residual --ymin=-0.55 --ymax=0.75

./plot_quilt.py --value=raw
./plot_quilt.py --value=fit --vmin=-3 --vmax=3
./plot_quilt.py --value=residual --vmin=-3 --vmax=3
