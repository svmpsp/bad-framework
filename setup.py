from setuptools import setup, find_packages
import bad_framework

with open('README.md', 'r') as fh:
    long_description = fh.read()

install_requirements = ['bad-client']

setup(
    name='bad-framework',
    version=bad_framework.__version__,
    author='Sivam Pasupathipillai',
    author_email='s.pasupathipillai@unitn.it',
    description='Benchmarking Anomaly Detection (BAD) framework.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        # 'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=install_requirements,
    python_requires='>=3.6',
)
