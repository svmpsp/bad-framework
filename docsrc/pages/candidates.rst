.. _pages/candidates:
   
Algorithms
==========
A Candidate is the abstraction representing an unsupervised anomaly
detection algorithm in the **BAD** framework.

In practice, a Candidate is a Python module implementing an anomaly
detection technique.

Default algorithms
------------------
The following table contains the default algorithm implementations available for **BAD**.

=========  =======
 Name       Source
=========  =======
 dummy      `Abnormal thyroid conditions <https://www.dbs.ifi.lmu.de/research/outlier-evaluation/DAMI/semantic/Annthyroid/>`_
 fb         `Forest cover types <http://odds.cs.stonybrook.edu/forestcovercovertype-dataset/>`_
 iforest    `Forensics glass samples <http://odds.cs.stonybrook.edu/glass-data/>`_
 knn        `Intrusion detection data set <https://www.dbs.ifi.lmu.de/research/outlier-evaluation/DAMI/literature/KDDCup99/>`_
 loci       `Hand-written digits <https://www.dbs.ifi.lmu.de/research/outlier-evaluation/DAMI/literature/PenDigits/>`_
 lof        `Space shuttle sensor reading <https://www.dbs.ifi.lmu.de/research/outlier-evaluation/DAMI/literature/Shuttle/>`_
 ocsvm      `Breast cancer screening <http://odds.cs.stonybrook.edu/wbc/>`_
 partknn    `Wine chemical analysis <http://odds.cs.stonybrook.edu/wine/>`_
=========  =======

Custom algorithms
-----------------
To implement an algorithm to be used by the **BAD** framework you must implement a Python
class, known as the *Candidate class*.

The Candidate class must be the *first class* (in order) to be defined in
the Candidate module.

The Candidate API defines the characteristics of the Candidate class.
In particular, a Candidate implementation must implement the following methods:

- **fit()**
- **score()**
- **__init__()**

The fit() method
________________
The **fit()** method must have the following signature:

.. code-block:: python

   def fit(self, train_data):

       # Perform model fitting ...

       return self

The **train_data** parameter represents the training dataset. It is represented as a
2-dimensional
`numpy array <https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.html>`_
of float with shape *N X D*.
The **fit()** method returns the fitted Candidate.

Even when the implemented algorithm does not require model fitting, e.g. stateless
models, you must still provide a **fit()** method with the given signature returning
the Candidate object instance.

The score() method
__________________
The **score()** method must have the following signature:

.. code-block:: python

   def score(self, element):

       # Compute score for data element ...

       return score


The **element** parameter represents a data element as a row vector.

Candidate initialization
________________________
Candidate initialization is performed using the **__init__()** method
of the Candidate class.

To support the :ref:`BAD parameters API <pages/parameters>`, the
Candidate **__init__()** method must be implemented with the following
signature.

.. code-block:: python

   def __init__(self, **kwargs):
   
       # Extract parameters from kwargs ...

The keys in the **kwargs** dict will match the keys defined in the
*candidate_parameters.txt* file. For more details, see
:ref:`hyper-parameter tuning <pages/parameters>`.

The special key *seed* is always provided by the framework to be used
as an RNG seed for replicable experiments. You can override the seed
in the Candidate parameters file.
