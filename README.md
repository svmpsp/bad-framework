# BAD - Benchmarking Anomaly Detection
The **BAD** framework is a distributed framework for benchmarking unsupervised anomaly detection algorithms.

For details, please refer to the **[official documentation](https://passiv-me.github.io/bad-framework/)**.

Installation
------------
**BAD** can be easily installed via `pip` with the command:

```
pip install bad-framework
```
this installs the `bad` command-line interface.

Example usage
-------------
Before running experiments, you need to start the **BAD** server processes:

```
bad server-start
```
Then, you can run a simple experiment with:

```
bad run -c lof -d shuttle
```
this executes the famous **Local Outlier Factor (LOF)** algorithm on the **shuttle** dataset.

By default, results are stored in the file `./bad_out.csv`.

The output file contains execution times, hyperparameter settings and evaluation metrics for all executed experiments.

The output file can be easily plotted with any graphing library.

Please refer to the **[official documentation](https://passiv-me.github.io/bad-framework/)** for a complete command line reference.

---

Copyright © 2020 Sivam Pasupathipillai - <sivam.pasupathipillai@gmail.com>.

All rights reserved.
