.. _pages/candidate:
   
Algorithms
==========

A Candidate is the abstraction representing an unsupervised anomaly
detection algorithm in the BAD framework.

In practice, a Candidate is a python module implementing an anomaly
detection technique.

The Candidate API defines the characteristics of a Candidate module.

The score method
----------------

A Candidate must implement the **score** method, with the following
signature:

.. code-block:: python

   def score(self, data_matrix):

       # Compute outlier scores ...

       return score_matrix

The **data_matrix** parameter represents the data set to be
analyzed. It is represented as a 2-dimensional `numpy array
<https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.html>`_
of float with shape *N X D*.

The **score_matrix** variable represents the output of the
algorithm. It should be a 2-dimensional `numpy array
<https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.html>`_
of float with shape *N X (D+1)*.  The additional column corresponds to
the score for each element.

As an example, when analyzing a data set with 100 data elements and 4
dimensions, BAD will enforce that:

.. code-block:: python

   >>> data_matrix.shape
   (100, 4)

While the Candidate code must enforce that:

.. code-block:: python

   >>> score_matrix.shape
   (100, 5)

Candidate class definition
--------------------------

The **score** method must be implemented as part of a class. The class
implementing the **score** method is called the *Candidate class*.

The Candidate class must be the **first class** (in order) defined in
the candidate module. The name of the Candidate class is used by the
BAD framework as an identifier.

There is no limit on the number of classes that can be defined in the
Candidate module, however the first class found in the module must
represent a Candidate, i.e. it must implement the score method.

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

Contributing Candidates
-----------------------

TODO
