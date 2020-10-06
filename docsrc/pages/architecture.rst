.. _pages/architecture:
   
BAD architecture
================

The BAD framework relies on a collection of independent processes organized as a master-worker architecture.

The main components of the framework are:

- **BAD client -** user facing application that is responsible for initialization, parameter settings and candidate files.
- **BAD master -** master server process. Responsible for communicating with the client, storing experiment results and initializing and orchestrating workers.
- **BAD worker(s) -** worker server process (one or several). Responsible for running the experiments and computing the anomaly detection results.

In order to use BAD, the user interacts with a BAD client (for example the :ref:`BAD CLI <pages/usage>`) in order to configure, initialize and communicate with the BAD server processes.

After initialization, the user can also communicate with the **BAD master** directly via a web browser, in order to inspect experiment results and monitor execution.

