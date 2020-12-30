"""Copyright (C) 2020 Sivam Pasupathipillai <s.pasupathipillai@unitn.it>.

All rights reserved.
"""
from setuptools import setup, find_packages
import bad_framework

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requirements = [
    "httpx",
    "Jinja2",
    "matplotlib",
    "numpy",
    "pyod",
    "requests",
    "scikit-learn",
    "tornado",
]

setup(
    name="bad-framework",
    version=bad_framework.__version__,
    author="Sivam Pasupathipillai",
    author_email="sivam.pasupathipillai@gmail.com",
    description="Benchmarking Anomaly Detection (BAD) framework.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        # 'License :: OSI Approved :: MIT License',
        "Operating System :: OS Independent",
    ],
    install_requires=install_requirements,
    python_requires=">=3.6",
    entry_points={"console_scripts": ["bad = bad_framework.bad_client:main"]},
    include_package_data=True,
)
