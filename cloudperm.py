#!/usr/bin/env python3
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from builtins import str
from future import standard_library
standard_library.install_aliases()
import httplib2
import os
import sys

from pathlib import Path

from googleapiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools 

import sqlite3
from sqlite3 import Error

import time
from datetime import datetime

from configparser import SafeConfigParser

import pprint

import re
import argparse

cloudperm_argparser = argparse.ArgumentParser(parents=[tools.argparser], add_help=False)
cloudperm_argparser.add_argument('--credential-directory', '-D', type=str, default='~/.credentials', help='Specify a credentials directory (default: ~/.credentials)')
#flags = cloudperm_argparser.parse_args()

#SCOPES = 'https://www.googleapis.com/auth/drive.metadata.readonly'
SCOPES = 'https://www.googleapis.com/auth/drive'
APPLICATION_NAME = 'CloudPerm'

def get_credentials(flags):
    """Gets valid user credentials from storage.
    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.
    Returns:
        Credentials, the obtained credential.
    """
    credential_dir = os.path.expanduser(flags.credential_directory)
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'gdrive-auth-token.json')
    client_secret_file = os.path.join(credential_dir, 'client_secret.json');

    store = file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(client_secret_file, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        print('Storing credentials to ' + credential_path)
    return credentials

def retrieve_permissions(service, file_id):
    
    """Retrieve a list of permissions.

    Args:
        service: Drive API service instance.
        file_id: ID of the file to retrieve permissions for.
    Returns:
    List of permissions.
    """
    try:
        permissions = service.permissions().list(fileId=file_id).execute()
        return permissions.get('items', [])
   
    except errors.HttpError as error:
        print ('An error occurred: %s' % error)
    return None
    
#used in permissionList
def retrieve_document_title(service, file_id):
    """Retrieve the title of the document.

    Args:
        service: Drive API service instance.
        file_id: ID of the file to retrieve the title for.
    Returns:
    The title of the document
    """

    try:
        filemetadata = service.files().get(fileId=file_id).execute()
        return filemetadata['title']
    except errors.HttpError as error:
        print ('An error occured: %s' % error)
    return None
   
#used for permissions list 
def retrieve_document_parents(service, file_id):
    # Call my parents! Call my parents! Call my parents! *stomp* *stomp* *stomp*
    """Retrieve the parents of the document.

    Args:
        service: Drive API service instance.
        file_id: ID of the file to retrieve the parents for
    Returns:
    List of parents
    """
    try:
        filemetadata = service.files().get(fileId=file_id).execute()
        return filemetadata['parents']
    except errors.HttpError as error:
        print ('An error occured: %s' % error)
    return None

def retrieve_all_files(service):
    """List all files using a google API query with no starting position.
       This does not work because Google has a documented API limit of 1000 and
       an undocumented API limit of 460. See get_files_in_folder() instead.
    """
    result = []
    page_token = None
    #for batch processing the limit is 100 
    while True:
        try:
            param = {}
            param['maxResults'] = 1000
            param['q'] = "mimeType='image/jpeg'"
            if page_token:
                param['pageToken'] = page_token
            files = service.files().list(**param).execute()

            print("List files returned " + str(len(list(files.keys()))) + " this time");

            result.extend(files['items'])
            page_token = files.get('nextPageToken')
            param['pageToken'] = page_token
            print("Next page token is " + page_token);
            if not page_token:
                break
        except errors.HttpError as error:
            print('An error occurred: %s' % error)
            break
        return result

def get_files_in_folder(service, folder_id):
    """Return an array of all the entities in a folder.
    """
    result = []
    page_token = None
    pp = pprint.PrettyPrinter(indent=4)

    while True:
        try:
            param = {}
            param['maxResults'] = 1000
            param['q'] = "'" + folder_id + "' in parents"

            if page_token:
                param['pageToken'] = page_token
            files = service.files().list(**param).execute()

            result.extend(files['items'])
            page_token = files.get('nextPageToken')
            param['pageToken'] = page_token
            if not page_token:
                break
        except errors.HttpError as error:
            print('An error occurred while retrieving files in folder %s: %s' % (folder_id,error))
            break
    return result 
                #   Proof to me that python indentation requirement is stupid. I spent 2 hours trying to figure out why this
                #   this function was returning nothing only to realize that I didn't have my return statement in the 
                #   right place because I didn't notice where it was. With brackets, I would have noticed this mistake.
    # return files['items']
    
##called in listFiles 
def walk_folders(service, folder_id, depth=0, excluded_folder_ids=[]):
    allfiles = []
    pp = pprint.PrettyPrinter(indent=4)
    files = get_files_in_folder(service, folder_id)  
    allfiles.extend(files)
    for file_entry in files:
        file_mimetype = file_entry['mimeType']
        file_id = file_entry['id']
        if file_mimetype == 'application/vnd.google-apps.folder' and (depth > 0) and file_id not in excluded_folder_ids:
            allfiles.extend(walk_folders(service, file_id, depth - 1, excluded_folder_ids))
    return allfiles

#called in listFiles 
def build_first_path(service, file_id):
    """Build the full path of the first parent in the list of parents
    """
    result = ""
    isroot = 0;
    directory_separator = u" \u25B6 "
    while isroot == 0:
        try:
            thefile = service.files().get(fileId=file_id).execute()
            if len(thefile['parents']) == 0:
                result = "[SHARED WITH YOU]" + directory_separator + result
                break
            else:
                parentfile = thefile['parents'][0] # Let's just use the first one for now. We'll handle multiple later.
                #print("parents: " + str(parentfile))
            if parentfile['isRoot'] == True:
                isroot = 1;
                result = thefile['title'] + directory_separator + result
                break
            else:
                #print("Going up a dir to " + parentfile['id'])
                result = thefile['title'] + directory_separator + result
                file_id = parentfile['id']
        except errors.HttpError as error:
            print('An error occured: %s' % error)
            break
    result = re.sub('/$', '', result)
    return result

#called in Revoke access
def revoke_document_role(service, file_id, role_id):
    # A non batch operation to revoke a specific permission.
    """Revoke a specific permission on a permission file.

    Args:
        service: Drive API service instance.
        file_id: file ID of the file to revoke the perm for.
        role_id: permission ID of the file to retrieve the parents for
    Returns:
    Empty on success
    """
    try:
        param = {}
        param['fileId'] = file_id
        param['permissionId'] = role_id
        # delete/revoke the permission from the document.
        returnval = service.permissions().delete(**param).execute()
        return returnval
    except errors.HttpError as error:
        print ('An error occured: %s' % error)

###make the database for comparison later 
def makeDB():
    
    conn = sqlite3.connect('listFiles.db')
    c = conn.cursor()
    files_table = '''CREATE TABLE IF NOT EXISTS files (fileID text PRIMARY KEY, fname text NOT NULL, modified_time smalldatetime, parent text NOT NULL)'''
    user_perm = '''CREATE TABLE IF NOT EXISTS user_perms (fileID text NOT NULL, email_address text NOT NULL, permission TEXT NOT NULL)'''
    # user_table = '''CREATE TABLE IF NOT EXISTS users (email text PRIMARY KEY, name text NOT NULL)'''

    # file_writers_table = '''CREATE TABLE IF NOT EXISTS file_writers (writer_email text NOT NULL, fileID text NOT NULL, revoked text, FOREIGN KEY (writer_email) REFERENCES users (email), FOREIGN KEY (fileID) REFERENCES files (fileID))'''
    # deleted_files = '''CREATE TABLE IF NOT EXISTS delete_files (fileID text NOT NULL)'''
    #tables to compare and track changes with 
    # deleted = '''CREATE TABLE IF NOT EXISTS deleted (fileID text NOT NULL)'''
    # changed_writers = '''CREATE TABLE IF NOT EXISTS writer_mods (writer_email text NOT NULL, fileID text NOT NULL)'''
    c.execute(files_table)
    c.execute(user_perm)
    # c.execute(file_writers_table)
    # c.execute(deleted)
    # c.execute(deleted_files)
    # c.execute(changed_writers)
    conn.commit()
    conn.close() 