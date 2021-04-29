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
   
    except:
        print ('Permissions not found')
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
    except:
        title = ""
        for i in file_id:
            title = title + i
        print ('File not found')
        conn = sqlite3.connect('listFiles.db')
        c = conn.cursor()

        delete = '''SELECT * FROM delete_files'''
        
        deleted= c.execute(delete)
        deleted= c.fetchall()
        dele = 0 
        for d_id in deleted:
            # print(d_id)
            # c.execute("UPDATE user_perms SET permission = ? WHERE fileID = ?", ("DELETED", str(d_id)))
            # conn.commit()
            if d_id == file_id:
                dele = 1
        if dele==1:
            c.execute("INSERT INTO delete_files (fileID) VALUES (?)", [str(title)])
            conn.commit()
            dele = 0
            
        
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
    except:
        print()
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

###make the database for comparison later 
def makeDB():
    
    conn = sqlite3.connect('listFiles.db')
    c = conn.cursor()
    files_table = '''CREATE TABLE IF NOT EXISTS files (fileID text PRIMARY KEY, fname text NOT NULL, modified_time smalldatetime, parent text NOT NULL)'''
    user_perm = '''CREATE TABLE IF NOT EXISTS user_perms (fileID text NOT NULL, email_address text NOT NULL, permission TEXT NOT NULL)'''
    temp_perm= '''CREATE TABLE IF NOT EXISTS temp_perms (fileID text NOT NULL, email_address text NOT NULL, permission TEXT NOT NULL)'''

    new_files = '''CREATE TABLE IF NOT EXISTS file_update (fileID text PRIMARY KEY, fname text NOT NULL, modified_time smalldatetime, parent text NOT NULL)'''
    perm_update = '''CREATE TABLE IF NOT EXISTS perm_update (fileID text NOT NULL, email_address text NOT NULL, permission TEXT NOT NULL)'''
    deleted_files = '''CREATE TABLE IF NOT EXISTS delete_files (fileID text)'''

    # c.execute("DROP TABLE file_update")
    # conn.commit()
    #tables to compare and track changes with 
    # deleted = '''CREATE TABLE IF NOT EXISTS deleted (fileID text NOT NULL)'''
    # changed_writers = '''CREATE TABLE IF NOT EXISTS writer_mods (writer_email text NOT NULL, fileID text NOT NULL)'''
    c.execute(files_table)
    c.execute(user_perm)
    c.execute(temp_perm)
    c.execute(new_files)
    c.execute(perm_update)
    c.execute(deleted_files)
    # c.execute(changed_writers)
    conn.commit()
    conn.close() 

def listFile(folderids, args = None):
     #create a dictionary 
    listFileDict = {} 
    folderids=[]

    tot_files=0    
    
    # # Get our list of file IDs.
    key = 0

    ##open database connection 
    conn = sqlite3.connect('listFiles.db')
    c = conn.cursor() 

    for start_folder_id in folderids:
        #calling walk_folders from cloudperm.py-> executes query through API 
        returnedfiles = walk_folders(service, start_folder_id, depth, args.exclude_folder)
        if type(returnedfiles) == list:
            for fileitem in returnedfiles:
                #pp.pprint(fileitem)
                path = build_first_path(service,fileitem['id'])
                #need this for writing to files, otherwise weird chatacters are created and will make it more work to use data in .csv/.tsv/.json
                path = path.replace("▶", ">")
                #not sure what this is doing exactly (think managing/formatting data)
                if args.show_mime_type:
                    outputline = "{1:<45} {0} {2:<45} {0} {3}\n".format(fieldsep, fileitem['id'], fileitem['mimeType'], path)
                    listFileDict[tot_files]= (fileitem['id'], fileitem['mimeType'], path)
                if args.long_list:
                    ownerlist = ",".join(fileitem['ownerNames'])
                    lastmodified = fileitem['modifiedDate']
                    parent_list = fileitem['parents']
                    parent = parent_list[0]['id']
                    outputline = "{1:<45} {0} {2:<25} {0} {3} {0} {4}\n".format(fieldsep, fileitem['id'], ownerlist,  lastmodified, path)
                    listFileDict[tot_files]= (fileitem['id'], ownerlist,  lastmodified, path)
                    c.execute("INSERT INTO files (fileID, fname, modified_time, parent) VALUES (?,?,?,?,)", (fileitem['id'], fileitem['title'], lastmodified, parent))
                    conn.commit() 
                else: 
                    outputline = "{1:<45} {0} {2}\n".format(fieldsep, fileitem['id'], path)
                    listFileDict[tot_files]=(fileitem['id'], path)
                
                sys.stdout.write(outputline)
                
                tot_files+=1
                
    print("Total files: " + str(tot_files))

    

    #write .json file 
    with open('listFiles.json', 'w') as json_file:
        json.dump(listFileDict, json_file)

#csv file create and write
    with open('listFiles.csv', 'w') as csv_file:
        csvwriter = csv.writer(csv_file)
        #create header row???
        #write dictionary to .csv
        for i in range(len(listFileDict)):
            csvwriter.writerow(listFileDict[i])
            i+=1
    
    #create and write TSV files   
    with open('listFiles.tsv', 'w') as tsv_file:
        tsvWriter = csv.writer(tsv_file, delimiter='\t')
        #create header row
        
        #write dictionary to .tsv
        for j in range(len(listFileDict)):
            tsvWriter.writerow(listFileDict[j])
            j+=1
            
    #things to think about adding:    
    #create headers 
    #write out listFileDict data to the csv
    #write out total files 


def permission(fileids, service):
    makeDB()

    # http = credentials.authorize(httplib2.Http())
    # service = discovery.build('drive', 'v2', http=http)
    
    for fileid in fileids:
        title = retrieve_document_title(service, fileid);
    print("Document Title: " + str(title));
    perm_list = retrieve_permissions(service, fileid)
    parents = retrieve_document_parents(service, fileid)
    #print("Parents: " + str(parents))
    
    
    #set up dictionary to export to files 
    count = 0 
    perm_dict = {}

    ##open database connection 
    conn = sqlite3.connect('listFiles.db')
    c = conn.cursor()
    
    try:
        for entry in perm_list:
            if type(entry) is dict:
                if 'emailAddress' in entry:
                    print("  " + entry['role'] + ":  " + entry['emailAddress']);

                    c.execute("INSERT INTO temp_perms (fileID, email_address, permission) VALUES (?,?,?)", (fileid, entry['emailAddress'], entry['role']))
                    conn.commit() 

                    perm_dict[count] = (title, fileid, entry['name'], entry['role'], entry['emailAddress'])
                else: # This probably is an entry that implies anyone with link or public.
                    #print("Entry json: " + str(entry));
                    if (entry['type'] == 'anyone' and entry['id'] == 'anyoneWithLink'):
                        warning1= " WARNING: ANYONE WITH THE LINK CAN READ THIS DOCUMENT."
                        print(warning1)
                        perm_dict[count] = (warning1)
                    elif (entry['type'] == 'anyone' and entry['id'] == 'anyone'):
                        warning2 = "  WARNING: THIS DOCUMENT IS PUBLIC AND CAN BE FOUND AND READ BY ANYONE WITH A SEARCH."
                        print(warning2)
                        perm_dict[count] = (warning2)
                    elif (entry['type'] == 'domain'):
                        permitted_domain = entry['domain'];
                        domain_allowed_role = entry['role'];
                        warning3 = "  WARNING: ANYONE FROM THE DOMAIN '" + permitted_domain + "' HAS '" + domain_allowed_role + "' PERMISSION TO THIS DOCUMENT."
                        print(warning3)
                        perm_dict[count] = (warning2)
                    else:
                        # Handle the unknown case in a helpful way.
                        warning4 =" Unknown permission type:"
                        print(warning4)
                        perm_dict[count] = (warning4)
                        pp = pprint.PrettyPrinter(indent=8,depth=6)
                        pp.pprint(entry);
                count +=1
        print()
        print()

    except:
        entry = "   "

    ####queries to compare 
    new = '''SELECT * FROM temp_perms'''
    existing = '''SELECT * FROM user_perms'''
    delete = '''SELECT * FROM delete_files'''

    new_perms= c.execute(new)
    new_perms= c.fetchall()

    existing_perms= c.execute(existing)
    existing_perms= c.fetchall()

    deleted= c.execute(delete)
    deleted= c.fetchall()
        

    #does any data need to be updated here? 
    match = 0
    #user in original permissions
    for user in existing_perms:
        ###is the docID and file ID the same?
        ###if not revoked
        ### if it is the same, update permission 
        for person in new_perms:
            if user == person:
                match = 1
                if match == 0:
                    if user[0] == person[0]:
                        if user[1] == person[1]:
                            ###update the permisson due to a permussuon change 
                            c.execute("UPDATE user_perms SET permission = ? WHERE fileID = ? AND email_address = ?", (person[2], user[0], user[1]))
                            conn.commit()
    
        match = 0

    #need to rerun the query since updates have been made to the databse, otherwise there is the potential for mismatch and data integrity compromise 
    existing_perms= c.execute(existing)
    existing_perms= c.fetchall()    

    ##insert new users with new documents into the database 
    perm_count = 0
    for i in new_perms:
        for j in existing_perms:
            if i == j:
                perm_count = 1
        #perform the insertion         
        if perm_count == 0:
             c.execute("INSERT INTO user_perms(fileID, email_address, permission) VALUES (?,?,?)", (i[0], i[1], i[2]))
             conn.commit()
        else:
            perm_count=0
    
    c.execute("DROP TABLE temp_perms")
    conn.commit()

    for item in deleted:
        # print()
        # print(item, "IN DELETED/permissions")
        # print()
        # what happens to user permissions if a file is deleted?
        c.execute("UPDATE user_perms SET permission = 'File Deleted' WHERE fileID = ?", [str(item[0])])
        conn.commit()


    #write .json file 
    with open('permList.json', 'w') as json_file:
        json.dump(perm_dict, json_file)

    #csv file create and write
    with open('permList.csv', 'w') as csv_file:
        csvwriter = csv.writer(csv_file)
        #create header row
        #write dictionary to .csv
        for i in range(len(perm_dict)):
            csvwriter.writerow(perm_dict[i])
            i+=1
    
    #create and write TSV files   
    with open('permList.tsv', 'w') as tsv_file:
        tsvWriter = csv.writer(tsv_file, delimiter='\t')
        #create header row
        #write dictionary to .tsv
        for j in range(len(perm_dict)):
            tsvWriter.writerow(perm_dict[j])
            j+=1   	
    
    return

def drop():
    ##open database connection 
    conn = sqlite3.connect('listFiles.db')
    c = conn.cursor()
    c.execute("DROP TABLE file_update")
    conn.commit()
    conn.close()
    return
