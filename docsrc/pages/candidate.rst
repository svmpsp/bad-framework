.. _pages/candidate:
   
Algorithms
==========

A Candidate is the abstraction representing an unsupervised anomaly
detection algorithm in the **BAD** framework.

In practice, a Candidate is a Python module implementing an anomaly
detection technique.

The Candidate API defines the characteristics of a Candidate module.

The score method
----------------

A Candidate must implement both the **fit()** and **score()** methods

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

The **score()** method must have the following signature:

.. code-block:: python

   def score(self, element):

       # Compute score for data element ...

       return score


The **element** parameter represents a data element as a row vector.

Candidate class definition
--------------------------

The **fit** and **score** methods must be implemented as a Python class.
This class is known as the *Candidate class*.

The Candidate class must be the *first class* (in order) defined in
the Candidate module.

Candidate initialization
------------------------

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
