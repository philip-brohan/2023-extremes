HadCRUT5 data download and access
=================================

Monthly average near-surface temperature anomalies, from in-situ observations (ships and stations), are available from `HadCRUT5 <https://www.metoffice.gov.uk/hadobs/hadcrut5>`_.

It's an ensemble dataset (100 members). We're going to compromise here and only use 20 members.

Script to do the whole download (about 600Mb). Only downloads data where it is not already on disc.

.. literalinclude:: ../../get_data/HadCRUT/get_members.py


Having downloaded the data, we need to use it. So we need some convenience functions to access the data.

Functions to access downloaded HadCRUT data:

.. literalinclude:: ../../get_data/HadCRUT/HadCRUT.py


