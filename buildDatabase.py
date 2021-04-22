#!/usr/bin/env python3

import sqlite3
from sqlite3 import Error

from cloudperm import *

# Add on any specific arguments that this program requires.
try:
    import argparse
    parser = argparse.ArgumentParser(parents=[cloudperm_argparser])
    parser.add_argument('documents', metavar='DocumentID', type=str, nargs='*', help='Google Document IDs')
    args = parser.parse_args()
except ImportError:
    args = None


def build():
    conn = sqlite3.connect('listFiles.db')
    c = conn.cursor() 
    ids= '''SELECT fileID FROM files'''
    fileids= c.execute(ids)
    fileids= c.fetchall()

    credentials = get_credentials(args)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v2', http=http)

    for file in fileids:
        permission(file, service)

build()
