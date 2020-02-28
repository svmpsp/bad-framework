from setuptools import setup, find_packages

with open('requirements.txt', 'r') as reqs_file:
    install_requirements = []
    for line in reqs_file:
        install_requirements.append(line.strip())

with open('README.md', 'r') as fh:
    long_description = fh.read()

print('Install requirements is', install_requirements)
    
setup(
    name='bad-framework',
    version='0.0.5',
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
