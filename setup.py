#!/usr/bin/env python3
# encoding: utf-8

# setuptools is a more powerful version of distutils
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from future import standard_library
standard_library.install_aliases()
try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(name='cloudperm',
      version='0.2',
      description="Cloud Storage Service permissions auditing software",
      author="Mark Krenz",
      url="https://github.com/deltaray/cloudperm",
      install_requires=[
          "google-api-python-client",
          "ConfigParser",
          "httplib2",
          "oauth2client",
          "urllib3"
      ],
      scripts=[
          'listFiles',
          'permissionList',
          'revokeAccess'
      ]
      )
