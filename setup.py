#!/usr/bin/env python
# encoding: utf-8

# setuptools is a more powerful version of distutils
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
