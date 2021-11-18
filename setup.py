#!/usr/bin/env python

from setuptools import setup

# This needs to have the following format - see Makefile 'upload' target.
VERSION = '1.0.4'

setup(name='pystdin',
      version=VERSION,
      include_package_data=False,
      url='https://github.com/terrycojones/pystdin',
      download_url='https://github.com/terrycojones/pystdin',
      author='Terry Jones',
      author_email='tcj25@cam.ac.uk',
      keywords=['python stdin standard input'],
      classifiers=[
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      license='MIT',
      scripts=['pystdin.py'],
      description=('Wrap command-line Python code in a loop over standard '
                   'input.'),
      extras_require={
        'dev': [
            'flake8',
            'pytest',
        ]
      })
