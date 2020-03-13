.. _pages/datasets:

Data sets
=========

BAD includes a collection of anomaly detection benchmark data sets.

All data sets are composed of numerical features only. All data sets are without duplicates.

============  =======  ============  =============================================================================================================================
 Name          Size     Dimensions    Description
============  =======  ============  =============================================================================================================================
 annthyroid    7129     21            Abnormal thyroid conditions `(source) <https://www.dbs.ifi.lmu.de/research/outlier-evaluation/DAMI/semantic/Annthyroid/>`_
 covertype     286048   10            Forest cover types `(source) <http://odds.cs.stonybrook.edu/forestcovercovertype-dataset/>`_
 glass         213      9             Forensics glass samples `(source) <http://odds.cs.stonybrook.edu/glass-data/>`_
 kdd99         48133    40            Intrusion detection data set `(source) <https://www.dbs.ifi.lmu.de/research/outlier-evaluation/DAMI/literature/KDDCup99/>`_
 pendigits     9868     16            Hand-written digits `(source) <https://www.dbs.ifi.lmu.de/research/outlier-evaluation/DAMI/literature/PenDigits/>`_
 shuttle       1013     9             Space shuttle sensor reading `(source) <https://www.dbs.ifi.lmu.de/research/outlier-evaluation/DAMI/literature/Shuttle/>`_
 wbc           377      30            Breast cancer screening `(source) <http://odds.cs.stonybrook.edu/wbc/>`_
 wine          129      13            Wine chemical analysis `(source) <http://odds.cs.stonybrook.edu/wine/>`_
============  =======  ============  =============================================================================================================================

Contributing benchmarks
-----------------------
If you want to contribute a benchmark data set to BAD it is important to do the following.

Your benchmark must be formatted in ARFF_. All data must be included into a single *.arff* file.

The first two attributes in the file must be named **id** and **outlier** where

- **id -** an integer identifier for the data element (starting from 0).
- **outlier -** represents the data element label, with outliers labeled as 1.0 and inliers labeled as 0.0.

All other attributes in the data set must be **real-valued**.

For example, you could contribute the file **my_data.arff** with the following content:

.. code-block:: bash

   @RELATION 'My custom dataset'

   @ATTRIBUTE 'id' integer
   @ATTRIBUTE 'outlier' real
   @ATTRIBUTE 'att1' real
   @ATTRIBUTE 'att2' real
   ...

See :ref:`Contributing to BAD <pages/contributions>` for more information.

.. _ARFF: https://www.cs.waikato.ac.nz/ml/weka/arff.html
