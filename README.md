# bad-framework: research framework for Benchmarking Anomaly Detection (BAD)
The BAD framework (**bad_framework**) is a distributed benchmarking framework for benchmarking unsupervised anomaly detection algorithms.

## SECURITY DISCLAIMER
BAD is a research prototype and is not meant to run on production systems.

BAD is **INSECURE by DESIGN** as it enables malicious users to run arbitrary code on the host running the BAD master (localhost by default).

**DO NOT** run 
> $ bad start-server

on hosts exposed to public networks, or on production critical systems.

## Installation
We recommend installing BAD inside a virtualenv.

To create and activate the virtualenv run:

> $ virtualenv --python=python3 bad-venv

To activate the virtualenv run

> $ source venv_bad/bin/activate

Then, install BAD inside the virtualenv using pip with:

> pip install bad-framework

To check if BAD is installed run:

> bad -h

This should print the command usage.

## Usage
BAD requires a set of some configuration files in order to run correctly.

BAD can create a default configuration with

> bad init

This command overwrites previous configuration files in the current directory, to avoid naming collision and data losses, we recommend moving to and empty directory before running **init**

Create a new directory with:
> $ mkdir bad-installation && cd bad-installation

Then initialize the BAD framework with:
> $ bad init

Your current directory should now contain the following files.
- conf/default.conf
- conf/workers
- candidate_parameters.txt
- candidate_requirements.txt
- candidates/ 

To start the BAD framework run:

> $ bad server-start

By default, this starts the BAD master on **localhost** at port **3290**.

A BAD worker is started on **localhost** at port **3291**.

You can check these processes are up and running by visiting the adresses:
- **localhost:3290**
- **localhost:3291**

with your browser.

You can run an example experiment with:
> $ bad -c candidates/LOF.py -d shuttle

By default, experiment results are saved to the **bad_dump.csv** file in the current directory.

Once you are done, you can stop the BAD framework with:

> $ bad server-stop


Copyright (c) 2020 Sivam Pasupathipillai <s.pasupathipillai@unitn.it>.

All rights reserved.
