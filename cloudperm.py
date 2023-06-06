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

#export processes
import csv
import json

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
SCOPES = 'https://www.googleapis.com/auth/drive'
######
credential_dir = ".credentials"
if not os.path.exists(credential_dir):
    os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'gdrive-auth-token.json')
    client_secret_file = os.path.join(credential_dir, 'client_secret.json');
    
store = file.Storage('storage.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store)
    credentials = creds
    
#######   
DRIVE = discovery.build('drive', 'v3', http=creds.authorize(Http()))       
APPLICATION_NAME = 'CloudPerm'
########

##############################################################
def get_credentials(flags):
    credentials = creds
    """Gets valid user credentials from storage.
    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.
    Returns:
        Credentials, the obtained credential.
    """        
    # Previously had some code here to get creds from gdrive-auth-token.json and client_secret.json
    # Removed by matt
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
            files = service.files().list(**param).execute() #lets try redoing this for batch processing ???/ not sure how maxResults fully works 

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

# Matt moved the following functions out of this file.
#   listFile()
#   permission()

#######New functionalities######### 
######################################################################################################
###DATABSE GLOBAL VARS
conn = sqlite3.connect('listFiles.db')
c = conn.cursor()
####modify api batch size here
#can be changed to up to 1000 --> will determine number of files/folders returned per batch request 
batch_size = 200 #global var ##200-400 recommended 
start_token = None
######################################################################################################

#make database    
def makeDB():
    
    conn = sqlite3.connect('listFiles.db')
    c = conn.cursor()
    files_table = '''CREATE TABLE IF NOT EXISTS files (fileID text PRIMARY KEY, name text NOT NULL, owner_email text NOT NULL, last_modifier text NOT NULL, modified_time smalldatetime, FOREIGN KEY (owner_email) REFERENCES users (email), FOREIGN KEY (last_modifier) REFERENCES users(email))'''
    users_table = '''CREATE TABLE IF NOT EXISTS users (email text PRIMARY KEY, name text NOT NULL)'''
    file_writers_table = '''CREATE TABLE IF NOT EXISTS file_writers (writer_email text NOT NULL, fileID text NOT NULL, revoked text, FOREIGN KEY (writer_email) REFERENCES users (email), FOREIGN KEY (fileID) REFERENCES files (fileID))'''
    deleted_files = '''CREATE TABLE IF NOT EXISTS delete_files (fileID text NOT NULL)'''
    #tables to compare and track changes with 
    deleted = '''CREATE TABLE IF NOT EXISTS deleted (fileID text NOT NULL)'''
    changed_writers = '''CREATE TABLE IF NOT EXISTS writer_mods (writer_email text NOT NULL, fileID text NOT NULL)'''
    c.execute(files_table)
    c.execute(users_table)
    c.execute(file_writers_table)
    c.execute(deleted)
    c.execute(deleted_files)
    c.execute(changed_writers)
    conn.commit()
    conn.close() 
    
# update database from last location     
def microUpdates(file_id, tokens, existing_files):    
    start_time = datetime.now()    
    page_token = tokens
    original_len = len(existing_files)
    id_list = existing_files
    
    while True: 
        if file_id is not None:
            api_results = DRIVE.files().list(q ='"'+ file_id + '" in parents', pageSize= batch_size, fields="nextPageToken, files(permissions, id, name, lastModifyingUser, modifiedTime)").execute()
        else:
            api_results = DRIVE.files().list(pageToken=page_token, pageSize= batch_size, fields="nextPageToken, files(permissions, id, name, lastModifyingUser, modifiedTime)").execute()
        page_token = api_results.get('nextPageToken', None)
        all_items = api_results.get('files', [])  
        
        ###do work with  data
        filter_data(all_items, id_list)
        
        # keep count of total files in query #think this through as files are constantly being added and deleted 1 for 1... 
        if original_len < len(id_list): 
            print()
            print("The number of new files found are:", len(id_list)-(original_len))
            original_len +=1 
            print("This update finished running at:", start_time)
            print()
            print()                    
        if page_token is None:
            break; 
    return

##sort through all data / do work 
def filter_data(data_set, file_list):
    all_items = data_set
    id_list = file_list
    for item in all_items:
        if item['id'] not in id_list:
            id_list.append(item['id'])
            c.execute("INSERT INTO deleted(fileID) VALUES(?)", [item['id']])
            conn.commit()
            print("File Data:", item['name'], item['id'], item['modifiedTime']) 
        #sort through the lists of dictionaries for permissions data abd print out important data 
        mod_count = 0 
        #access nested api reply and insert into normalized databse without repeats 
        for perm in item['permissions']:
            if perm['role'] == 'owner':
                #c.execute is for sqlite database work
                new_files = '''SELECT fileID from files'''
                new_res = c.execute(new_files)
                new_res= c.fetchall() 
                id_count = 0
                for id in new_res:
                    if item['id'] in id:
                        id_count += 1
                if id_count == 0:
                    c.execute("INSERT INTO files (name, fileID, owner_email, last_modifier, modified_time) VALUES (?,?,?,?,?)", (item['name'], item['id'], perm['emailAddress'], item['lastModifyingUser']['emailAddress'], item['modifiedTime']))
                    conn.commit()
                    id_count = 0
            else:  
                #make sure entry isn't already in database before adding to dB       
                changes = '''SELECT fileID FROM file_writers WHERE writer_email = ?'''
                perm_email = perm['emailAddress']
                res_changes= c.execute(changes, [perm_email])
                res_changes = c.fetchall() 
                perm_count = 0
                c.execute("INSERT INTO writer_mods(writer_email, fileID) VALUES (?, ?)", (perm['emailAddress'], item['id']))
                conn.commit()
                for eadd in res_changes:
                    if item['id'] in eadd: 
                        perm_count+=1
                if perm_count == 0:    
                    c.execute("INSERT INTO file_writers(writer_email, fileID) VALUES (?, ?)", (perm['emailAddress'], item['id']))
                    conn.commit()
                    perm_count = 0
            #make sure entry isn't already in database             
            user_data = '''SELECT email FROM users'''
            user_res = c.execute(user_data)
            user_res = c.fetchall()
            user_count = 0
            for us in user_res:
                if perm['emailAddress'] in us:
                    user_count +=1
            if user_count == 0:
                # print("Permissions:", perm['emailAddress'], perm['displayName'], [perm['role']])
                c.execute("INSERT INTO users (email, name) VALUES (?, ?)",  (perm['emailAddress'], perm['displayName']))
                conn.commit()
                user_count = 0
                         
        #get modification data for tampering
        #see if there have been new modifications, if not don't update the field in the dB
        mod_changes = '''SELECT modified_time from files WHERE fileID =?'''
        mod_data = item['id']
        moded = c.execute(mod_changes, [mod_data])
        moded = c.fetchall()
            
        for dif in moded:
            if item['modifiedTime'] in dif:
                mod_count +=1
            if mod_count == 0:
                print("Mod data", item['modifiedTime'], dif)
                up_last_mod = '''UPDATE files SET last_modifier = ? WHERE fileID = ?'''
                up_mod_time = '''UPDATE files SET modified_time = ? WHERE fileID = ?'''               
                c.execute(up_last_mod, (item['lastModifyingUser']['emailAddress'], item['id']))
                conn.commit()
                c.execute(up_mod_time,(item['modifiedTime'], item['id']))
                conn.commit()
                print("Modified Data:", item['lastModifyingUser']['displayName'], item['lastModifyingUser']['emailAddress'])
                print()
                print()   
            mod_count = 0   
                
    #comparing the files in the most recent run of the database to the files that were there/ looking for deleted files             
    all_IDs = '''SELECT fileID FROM deleted'''
    ids = c.execute(all_IDs)
    ids = c.fetchall() 
    up_IDs = '''SELECT fileID FROM files'''
    new_ids = c.execute(up_IDs)
    new_ids = c.fetchall()  
    del_files = c.execute('''SELECT fileID FROM delete_files''')
    del_files = c.fetchall()
    for id in new_ids:
        if id not in ids:
            if id not in del_files:
                print("New Files", id[0])
                c.execute('''INSERT INTO delete_files(fileID) VALUES(?)''', [id[0]])
                conn.commit()
                
    #looking for permission changes in the drive and updating database to match        
    user_perm = '''SELECT * FROM writer_mods'''
    us_perm = c.execute(user_perm)
    us_perm = c.fetchall()               
    update_perm= '''SELECT writer_email, fileID FROM file_writers'''
    up_perm= c.execute(update_perm)
    up_perm= c.fetchall()
    for item in up_perm:
        if item not in us_perm:
            write = '''UPDATE file_writers SET revoked = ? WHERE fileID = ? AND writer_email = ?'''
            c.execute(write, ("revoked", item[1], item[0]))
            conn.commit()
    conn.commit()       

makeDB()
