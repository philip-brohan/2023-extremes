Visualizations - anomaly time-series
====================================

.. figure:: ../../visualizations/plot_raw.webp
   :width: 95%
   :align: center
   :figwidth: 95%

   HadCRUT5 global mean temperature anomaly for each month since 1970. (Actually 20 plots, one for each ensemble member used - that's why it looks a bit fuzzy)


.. figure:: ../../visualizations/plot_raw_september.webp
   :width: 95%
   :align: center
   :figwidth: 95%

   Same plot, but for all Septembers (rather than all months).


Script (`plot_raw_ts.py`) to make both plots. (Add `--month=9` to make the Septembers only version)

.. literalinclude:: ../../visualizations/plot_raw_ts.py
    :language: bash

