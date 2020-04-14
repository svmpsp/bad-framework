.. BAD: benchmarking for anomaly detection documentation master file, created by
   sphinx-quickstart on Mon Nov 18 12:52:25 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to BAD: Benchmarking for Anomaly Detection!
===================================================

.. warning::
   **BAD** is **insecure** by design.

   **Do not deploy** in production critical systems or on open networks.
   Security features might be added in future releases.

BAD is a benchmarking framework for unsupervised anomaly detection
algorithms.

BAD's features include:

- a simple :ref:`command line interface <pages/usage>`.
- a collection of benchmark :ref:`data sets <pages/datasets>` from the
  literature.
- a convenient interface for :ref:`hyperparameter tuning
  <pages/parameters>`.
- out-of-the-box support for :ref:`distributed processing
  <pages/execution>`.
- extensibility via custom python modules implementing the
  :ref:`Candidate API <pages/candidate>`.

BAD is built with lots of ❤ and Python.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   pages/installation
   pages/usage
   pages/datasets
   pages/candidate
   pages/parameters
   pages/execution
   pages/contributions

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
