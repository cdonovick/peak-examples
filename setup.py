from setuptools import setup, find_namespace_packages
import sys

setup(
    name='peak-examples',
    version='0.0.1',
    url='https://github.com/cdonovick/peak-examples',
    license='MIT',
    maintainer='Caleb Donovick',
    maintainer_email='donovick@cs.stanford.edu',
    description='Example peak specifications',
    packages=find_namespace_packages(include=['examples', 'examples.*']),
    install_requires=[
        'peak @ git+https://github.com/cdonovick/peak#egg=peak',
    ],
)
