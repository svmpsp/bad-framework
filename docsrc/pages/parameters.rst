.. _pages/parameters:
   
Hyperparameter tuning
======================
BAD is designed to run a large number of experiments in parallel. This enables effective parameter searches.

The BAD parameter API was developed to be both intuitive and powerful.

Parameters should be specific for each :ref:`Candidate <pages/candidates>`.

The parameters API is used to define the experiments to be run by the BAD framework. Each parameter combination defines an experiment.

The Candidate parameters file
-----------------------------
All Candidate parameters are defined in the **.bad/candidate_parameters.txt** file.

This file contains a parameter setting for each line. The Candidate parameters file also supports line comments.

As an example, the following is a valid Candidate parameter file:

.. code-block:: python
   :caption: candidate_parameters.txt
   :linenos:

   # BAD candidate parameters file (this is a comment)
   x   10
   y   10   100  10
   z   1.0  2.0  0.1
   # ... this is another comment
   database_endpoint  http://mydb.url/instance1234 

Parameter value settings
------------------------
A value setting sets the value for a particular parameter key. The key and value must be separated by at least one whitespace character.

In the example, lines 2 and 6 define value settings.

Parameter range settings
------------------------
Range settings define a range of values between a minimum and maximum. Range settings support both integer and floating ranges.

The syntax to define a range setting is:

.. code-block:: python

   parameter_key   min_value   max_value   step

Each element of the definition must be separated by at least one whitespace character. Both the *min_value* and *max_value* values are included in the range.

Lines 3 and 4 in the example define range parameter settings. Line 3 defines a range setting for the **y** parameter. This defines one experiment for each value in the range for the parameter. In this case the range is:

.. code-block:: python

   y = [10, 20, 30, ... 100]

If the range between *min_value* and *max_value* cannot be exactly divided into an integer number of *steps* the behavior is undefined. For example, the behavior with the following definition is undefined:

.. code-block:: python

   weird_range   1   10   4

Parameter types
---------------
BAD supports integer, float and string parameter values. The actual type is determined at runtime casting the value to the most specific type (integer) and falling back to the more general type if the casting fails.

For example, the value '4' will be interpreted as an integer, the value '0.4' will be interpreted as a float, while the value '0.4float' will be interpreted as a string parameter.
