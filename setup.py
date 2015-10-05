#! /usr/bin/env python
import os
from setuptools import setup, find_packages

def get_readme():
    try:
        return open(os.path.join(os.path.dirname(__file__), 'README.md')).read()
    except IOError:
        return ''

setup(
    name='owndb',
    version='1.0.5',
    author='Hugo Castilho',
    author_email='hugo.p.castilho@telecom.pt',
    url='https://github.com/sapo/vulnmgt',
    description=('OwnDB is an app created to help pentest teams manage'
                 'vulnerabilities and audits.'),
    long_description=get_readme(),
    license='LICENSE',

    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    install_requires=[
        'MySQL-python',
        'bleach',
        'duplicates',
        'gunicorn',
        'issuesdb',
        'owndb-intra',
    ],
    zip_safe=False,
)
