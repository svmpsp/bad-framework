# BAD: a research framework for Benchmarking Anomaly Detection
The BAD framework (**bad_framework**) is a distributed benchmarking framework for unsupervised anomaly detection algorithms.

Please refer to the [official documentation](https://passiv-me.github.io/bad-framework/) for details.

## SECURITY DISCLAIMER
BAD is a research prototype and is not meant to run on production systems. BAD is **INSECURE by DESIGN** as it enables malicious users to run arbitrary code on the host running the BAD master (localhost by default).

**DO NOT** run 
> $ bad server-start

on hosts exposed to public networks, or on production critical systems.

## Installation
We recommend installing BAD inside a virtualenv.

To create and activate the virtualenv run:
> $ virtualenv --python=python3 .bad_venv

To activate the virtualenv run:
> $ source .bad_venv/bin/activate

Then, install BAD inside the virtualenv using pip with:
> $ pip install bad-framework

To check if BAD is installed run:
> $ bad -h

which should print the command usage.

## Usage
BAD requires a set of some configuration files in order to run correctly.

You can create a default configuration with:
> $ bad init

**WARNING:** the **bad init** command overwrites previous configuration files in the current directory.
 To avoid naming collision and data losses, we recommend moving to an empty directory before running **bad init**

Create a new directory with:
> $ mkdir bad-installation && cd bad-installation

Then initialize the BAD framework with:
> $ bad init

Your current directory should now contain the following files.
- **conf/default.conf -** default configuration settings.
- **conf/workers -** worker specification file.
- **candidate_parameters.txt -** Candidate hyperparameter file.
- **candidate_requirements.txt -** Candidate requirements file.
- **candidates/** - Candidate directory. It contains Candidate implementations

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
