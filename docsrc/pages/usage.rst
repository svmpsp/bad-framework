.. _pages/usage:
   
Usage
=====

.. code-block:: bash

   usage: bad [-h] [-c BAD.CANDIDATE] [-d BAD.DATA] [-o BAD.DUMP.FILE]
              [-p BAD.CANDIDATE.PARAMETERS] [-q BAD.CANDIDATE.REQUIREMENTS] [-v]
	      [{run,server-start,server-stop}]


The BAD CLI is the main client provided with the BAD framework. It enables users to control BAD processes and run experiments on the framework.

Basic commands
--------------
Commands are used to manage the BAD framework, all available commands are described in the following table.

================  ================================================================================================================================
 Command           Description
================  ================================================================================================================================
 run               Runs a suite of anomaly detection experiments.
 server-start      Starts BAD server processes. By default reads configuration settings from .bad/bad.conf and .bad/workers.
 server-stop       Stops BAD server processes. By default reads configuration settings from .bad/bad.conf and .bad/workers.
================  ================================================================================================================================

Execution
---------
Once the server processes are running, experiments can be executed with the following command:

.. code-block:: bash

   bad run -c candidate_name -o my_output_file.csv -d dataset_name

The number of experiments is determined by the candidate parameters file (by default .bad/candidate_parameters.txt).

A value parameter setting determines one experiment, while a range parameter settings determines an experiments for each value in the range.