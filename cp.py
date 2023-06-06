#!/usr/bin/env python3
from __future__ import print_function

from googleapiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools 

import sqlite3
from sqlite3 import Error

import time
from datetime import datetime

import argparse
cloudperm_argparser = argparse.ArgumentParser(parents=[tools.argparser], add_help=False)
cloudperm_argparser.add_argument('--credential-directory', '-D', type=str, default='~/.credentials', help='Specify a credentials directory (default: ~/.credentials)')
###################################################
###API set up
SCOPES = 'https://www.googleapis.com/auth/drive'
store = file.Storage('storage.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store)
DRIVE = discovery.build('drive', 'v3', http=creds.authorize(Http()))

###################################################
###DATABSE GLOBAL VARS
conn = sqlite3.connect('listFiles.db')
c = conn.cursor()
####modify api batch size here
#can be changed to up to 1000 --> will determine number of files/folders returned per batch request 
batch_size = 200 #global var
start_token = None
######################################################################################################

#make database    
def makeDB():
    
    conn = sqlite3.connect('listFiles.db')
    c = conn.cursor()
    files_table = '''CREATE TABLE IF NOT EXISTS files (fileID text PRIMARY KEY, name text NOT NULL, owner_email text NOT NULL, last_modifier text NOT NULL, modified_time smalldatetime, FOREIGN KEY (owner_email) REFERENCES users (email), FOREIGN KEY (last_modifier) REFERENCES users(email))'''
    users_table = '''CREATE TABLE IF NOT EXISTS users (email text PRIMARY KEY, name text NOT NULL)'''
    file_writers_table = '''CREATE TABLE IF NOT EXISTS file_writers (writer_email text NOT NULL, fileID text NOT NULL, FOREIGN KEY (writer_email) REFERENCES users (email), FOREIGN KEY (fileID) REFERENCES files (fileID))'''
    deleted = '''CREATE TABLE IF NOT EXISTS delete_files (fileID text NOT NULL)'''
    c.execute(files_table)
    c.execute(users_table)
    c.execute(file_writers_table)
    c.execute(deleted)
    conn.commit()
    conn.close() 
    
# update database from last location     
def microUpdates(tokens, existing_files):    
    conn = sqlite3.connect('listFiles.db')
    c = conn.cursor()
    start_time = datetime.now()    
    new_files = 0  
    page_token = tokens
    original_len = len(existing_files)
    id_list = existing_files
    
    while True: 
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
    conn.close() 
    return

##main argument of function 
def listFiles(token=None):
    #dB connection 
    conn = sqlite3.connect('listFiles.db')
    c = conn.cursor() 
    total_files = 0
    page_token = token
    
    #batch updates using pageTokens
    id_list = []
    count = 0
    while True: 
        api_results = DRIVE.files().list(pageToken=page_token, pageSize= batch_size, fields="nextPageToken, files(permissions, id, name, lastModifyingUser, modifiedTime)").execute()
        page_token = api_results.get('nextPageToken', None)
        if count > 0:
            if page_token is not None:
                last_page_token=page_token
                start_token = last_page_token
        else:
            last_page_token = None 
            start_token = last_page_token
        count+=1    
        
        all_items = api_results.get('files', [])
        
        filter_data(all_items, id_list)
        
        total_files = len(id_list)
        if page_token is None:
            print("The total files in the drive at this time are:", total_files)
            print()
            break;
    conn.close() 
    elapsed_time = 0
    
    #makes this application run continually 
    while True:
        time.sleep(2) #every 5 min ->>> 600 seconds
        microUpdates(last_page_token, id_list)
        elapsed_time +=1 
        if elapsed_time == 5: #approximately every 12 hours run listFiles all over -->>>>> if it calls microUpdate every 5 minutes, thats is 20x per hour. 20x#of hours you want between major runs
            id_list = []
            main()
    return; 

##sort through all data / do work 
def filter_data(data_set, file_list):
    all_items = data_set
    id_list = file_list
    for item in all_items:
        if item['id'] not in id_list:
            id_list.append(item['id'])
            print("File Data:", item['name'], item['id'], item['modifiedTime']) 
            #sort through the lists of dictionaries for permissions data abd print out important data 
            for perm in item['permissions']:
                if perm['role'] == 'owner':
                    #c.execute is for sqlite database work
                    c.execute("INSERT OR IGNORE INTO files (name, fileID, owner_email, last_modifier, modified_time) VALUES (?,?,?,?,?)", (item['name'], item['id'], perm['emailAddress'], item['lastModifyingUser']['emailAddress'], item['modifiedTime']))
                    conn.commit()
                else:
                    c.execute("INSERT OR IGNORE INTO file_writers(writer_email, fileID) VALUES (?, ?)", (perm['emailAddress'], item['id']))
                    conn.commit()
                    
                c.execute("INSERT OR IGNORE INTO users (email, name) VALUES (?, ?)",  (perm['emailAddress'], perm['displayName']))
                conn.commit()
                
                print("Permissions:", perm['emailAddress'], perm['displayName'], perm['role'])
                
            #get modification data for tampering 
            print("Modified Data:", item['lastModifyingUser']['displayName'], item['lastModifyingUser']['emailAddress'])
            print()
            print()                   
                 
def main():
    listFiles()       
    return
### think about implementation of change() function by Google 

#calls     
makeDB() 
main()


###program recognizes that there is a file deleted (must be perm deleted)
#how to handle? 
#if fileID was in last_ID list, but is not in id_list:
    #print fileID, fileName, dateModified? 
    #how do we want to flag?
        #could get bulky/resource consumption
    #false negaticves?
    #recovery is an issue
    #add fileID to new table??? <- seems like best solution 
#dateTime issues
#query results 
#updates and 

#SQL to look at file perms 

#finite statemachine 
#loop runs all the times based on what needs to happen 
#Change date object -> sql date object 
#unix epic time??? <- an option 