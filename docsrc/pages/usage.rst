.. _pages/usage:
   
Usage
=====

.. code-block:: bash

   usage: bad [-h] [-c BAD.CANDIDATE] [-q BAD.CANDIDATE.REQUIREMENTS]
              [-p BAD.CANDIDATE.PARAMETERS] [-d BAD.DATA] [-o BAD.DUMP.FILE]
              [-D BAD.CONFIGURATION] [-l BAD.LOG.LEVEL]
              [init | server-start | server-stop]

The BAD CLI is the main client provided with the BAD framework. It enables users to control BAD processes and run experiments on the framework.

Basic commands
--------------
Commands are used to manage the BAD framework, all available commands are described in Table XXX.

================  ================================================================================================================================
 Command           Description
================  ================================================================================================================================
 init              Initializes BAD configuration files in current directory
 server-start      Starts BAD server processes. By default reads configuration from conf/bad-defaults.conf and conf/workers
 server-stop       Stops BAD server processes. By default reads configuration from conf/bad-defaults.conf and conf/workers
================  ================================================================================================================================

Execution
---------
Once the server processes are running, experiments can be executed with the following command:

.. code-block:: bash

   bad -c my_candidate.py -o my_output_file.csv

This runs experiments using the Candidate module my_candidate.py and stores the results in CSV format to my_output_file.csv. The output file is also called a dump file.

The number of experiments is determined by the candidate parameters file (by default BAD_HOME/candidate_parameters.txt, overriden with the -p flag). 

A value parameter setting determines one experiment, while a range parameter settings determines an experiments for each value in the range. 

The total number of experiments is determined by multiplying the number of experiments for each parameter setting.
