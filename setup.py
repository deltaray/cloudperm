#!/usr/bin/env python
# encoding: utf-8

# setuptools is a more powerful version of distutils
try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(name='gdoc_perm_checker',
      version='0.1',
      description="Google drive permissions checker",
      author="Mark Krenz",
      url="https://github.com/deltaray/gdoc_perm_checker",
      install_requires=[
          "google-api-python-client",
          "ConfigParser",
          "httplib2",
          "oauth2client",
          "urllib3"
      ],
      scripts=[
          'listFiles.py',
          'permissionList.py'
      ]
      )
