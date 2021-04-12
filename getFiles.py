#!/usr/bin/env python3

from cloudperm import *

import sqlite3
from sqlite3 import Error

##main argument of function 
def getFiles(file_id=None):
    #dB connection 
    conn = sqlite3.connect('listFiles.db')
    c = conn.cursor() 
    total_files = 0
    page_token = None
    #batch updates using pageTokens
    id_list = []
    count = 0
    while True:
        if file_id is not None:
            api_results = DRIVE.files().list(q ='"'+ file_id + '" in parents', pageSize= batch_size, fields="nextPageToken, files(permissions, id, name, lastModifyingUser, modifiedTime)").execute()
        else:
            api_results = DRIVE.files().list(pageToken=page_token, pageSize= batch_size, fields="nextPageToken, files(permissions, id, name, lastModifyingUser, modifiedTime)").execute()
        page_token = api_results.get('nextPageToken', None)
        if count > 0:
            if page_token is not None:
                last_page_token=page_token
        else:
            last_page_token = None 
        count+=1     
        all_items = api_results.get('files', [])
        filter_data(all_items, id_list)
        total_files = len(id_list)
        if page_token is None:
            print("The total files in the drive at this time are:", total_files)
            print()
            break;
    elapsed_time = 0
    
    #makes this application run continually 
    while True:
        time.sleep(2) #every 5 min ->>> 600 seconds
        microUpdates(file_id, last_page_token, id_list)
        elapsed_time +=1 
        if elapsed_time == 5: #approximately every 12 hours run listFiles all over -->>>>> if it calls microUpdate every 5 minutes, thats is 20x per hour. 20x#of hours you want between major runs
            id_list = []
            c.execute('''DELETE FROM deleted''')
            c.execute('''DELETE FROM writer_mods''')
            conn.commit()
            conn.close()
            main()

#main funtion                 
def main(file_ID=None):
    getFiles()      
    return

#clean up the ending of Cloudperm 
try:   
    #calls   
    makeDB() 
    main()
except KeyboardInterrupt:
    print()
    print("You have quit Cloudperm")
    exit()