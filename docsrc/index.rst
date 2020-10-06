.. BAD: benchmarking for anomaly detection documentation master file, created by
   sphinx-quickstart on Mon Nov 18 12:52:25 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

BAD: Benchmarking for Anomaly Detection
=======================================

.. warning::
   The **BAD framework** lets users execute **arbitrary code** on the server machine.

   **DO NOT** deploy on production critical systems or open networks.
   Security features might be added in future releases.

**BAD** is a benchmarking framework for unsupervised anomaly detection.

With **BAD** you can:

- quickly test/prototype anomaly detection algorithms written in Python.
- compare different algorithms on a collection of well-established benchmarks.
- rapidly find the best hyperparameter settings for your algorithm.

**BAD**'s features include:

- a simple :ref:`command line interface <pages/usage>`.
- a collection of benchmark :ref:`data sets <pages/datasets>` from the
  literature.
- a convenient interface for :ref:`hyperparameter tuning <pages/parameters>`.
- out-of-the-box support for :ref:`distributed processing <pages/architecture>`.
- extensibility via custom python modules implementing the
  :ref:`Candidate API <pages/candidates>`.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   pages/installation
   pages/usage
   pages/datasets
   pages/candidates
   pages/parameters
   pages/architecture
   pages/contributions

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

**BAD** is built with lots of ❤ and Python.
