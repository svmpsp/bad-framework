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

=========  ===========================================================================================
 Name       Source
=========  ===========================================================================================
 dummy      Random anomaly detector
 fb         `Feature bagging <https://dl.acm.org/doi/abs/10.1145/1081870.1081891>`_
 iforest    `Isolation forest <https://ieeexplore.ieee.org/abstract/document/4781136>`_
 knn        `K-nearest neighbor anomaly detector <https://dl.acm.org/doi/abs/10.1145/342009.335437>`_
 loci       `Local correlation integral <https://ieeexplore.ieee.org/abstract/document/1260802>`_
 lof        `Local outlier factor <https://dl.acm.org/doi/abs/10.1145/342009.335388>`_
 ocsvm      `One-class SVM <https://www.mitpressjournals.org/doi/abs/10.1162/089976601750264965>`_
 partknn    Partition-wise k-nearest neighbor
=========  ===========================================================================================

Custom algorithms
-----------------
To implement an algorithm to be used by the **BAD** framework you must implement a Python
class, known as the *Candidate class*.

The Candidate class must be the *first class* (in order) to be defined in
the Candidate module.

The Candidate API defines the characteristics of the Candidate class.
In particular, a Candidate implementation must implement the following methods:

- **__init__()**
- **fit()**
- **score()**

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
:ref:`Hyperparameter tuning <pages/parameters>`.

The special key *seed* is always provided by the framework to be used
as an RNG seed for replicable experiments. You can override the seed
in the Candidate parameters file.

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
