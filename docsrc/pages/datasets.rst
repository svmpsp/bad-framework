.. _pages/datasets:

Datasets
========

BAD includes a collection of anomaly detection benchmark datasets.

All data sets are composed of numerical features only. All datasets are without duplicates.

============  =======  ============  =============================================================================================================================
 Name          Size     Dimensions    Description
============  =======  ============  =============================================================================================================================
 annthyroid    7129     21            `Abnormal thyroid conditions <https://www.dbs.ifi.lmu.de/research/outlier-evaluation/DAMI/semantic/Annthyroid/>`_
 covertype     286048   10            `Forest cover types <http://odds.cs.stonybrook.edu/forestcovercovertype-dataset/>`_
 glass         213      9             `Forensics glass samples <http://odds.cs.stonybrook.edu/glass-data/>`_
 kdd99         48133    40            `Intrusion detection data set <https://www.dbs.ifi.lmu.de/research/outlier-evaluation/DAMI/literature/KDDCup99/>`_
 pendigits     9868     16            `Hand-written digits <https://www.dbs.ifi.lmu.de/research/outlier-evaluation/DAMI/literature/PenDigits/>`_
 shuttle       1013     9             `Space shuttle sensor reading <https://www.dbs.ifi.lmu.de/research/outlier-evaluation/DAMI/literature/Shuttle/>`_
 wbc           377      30            `Breast cancer screening <http://odds.cs.stonybrook.edu/wbc/>`_
 wine          129      13            `Wine chemical analysis <http://odds.cs.stonybrook.edu/wine/>`_
============  =======  ============  =============================================================================================================================

Contributing benchmarks
-----------------------
If you want to contribute a benchmark dataset to BAD, please ensure the following:

1. your benchmark is formatted in ARFF_. All data must be included into a single *.arff* file.
2. the first two attributes in the file must be named **id** and **outlier**, where:

- **id -** an integer identifier for the data element (starting from 0).
- **outlier -** represents the data element label, with outliers labeled as 1.0 and inliers labeled as 0.0.

3. All other attributes in the dataset must be **real-valued**.

For example, you could contribute the file **my_data.arff** with the following content:

.. code-block:: bash
   :caption: Contents of my_data.arff

   @RELATION 'My custom dataset'

   @ATTRIBUTE 'id' integer
   @ATTRIBUTE 'outlier' real
   @ATTRIBUTE 'att1' real
   @ATTRIBUTE 'att2' real
   ...

See :ref:`Contributing to BAD <pages/contributing>` for more information.

.. _ARFF: https://www.cs.waikato.ac.nz/ml/weka/arff.html
