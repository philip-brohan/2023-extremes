Get the data to be used
=======================

We want observations of global near-surface temperatures, so `HadCRUT5 <https://www.metoffice.gov.uk/hadobs/hadcrut5>_`:

.. toctree::
   :titlesonly:
   :maxdepth: 1

   Download and access HadCRUT5 data <HadCRUT>

We also want a land-sea mask (for plotting only). We will use a land-surface only variable from ERA5-land for this (we only need one month). If we needed it to model the data it would be necessary to choose a land-mask that matched the data resolution and grid, but for plotting purposes we can use anything.

.. toctree::
   :titlesonly:
   :maxdepth: 1

   Download the land mask <land_mask>

Convenience script to download all the data:

.. literalinclude:: ../../get_data/download_all_data.sh


