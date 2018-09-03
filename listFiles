#!/usr/bin/python

from __future__ import print_function
import httplib2
import os
import sys
import re

from ConfigParser import SafeConfigParser

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

from apiclient import errors

# From https://wiki.python.org/moin/PrintFails
# Python tries to be too pedantic and ends up failing royally.
# So we have to do this so that we can do things like pipe output to other commands.
import sys, codecs, locale;
sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout);


import pprint
# ...


#try:
#    import argparse
#    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
#except ImportError:
#    flags = None

SCOPES = 'https://www.googleapis.com/auth/drive.metadata.readonly'
CLIENT_SECRET_FILE = '~/.credentials/client_secret.json'
APPLICATION_NAME = 'Drive API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def retrieve_all_files(service):
    """List all files using a google API query with no starting position.
       This does not work because Google has a documented API limit of 1000 and
       an undocumented API limit of 460. See get_files_in_folder() instead.
    """
    result = []
    page_token = None

    while True:
        try:
            param = {}
            #param['maxResults'] = 1000
            param['maxResults'] = 1000
            param['q'] = "mimeType='image/jpeg'"
            if page_token:
                param['pageToken'] = page_token
            files = service.files().list(**param).execute()

            print("List files returned " + str(len(files.keys())) + " this time");

            result.extend(files['items'])
            page_token = files.get('nextPageToken')
            param['pageToken'] = page_token
            print("Next page token is " + page_token);
            if not page_token:
                break
        except errors.HttpError, error:
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
            # Just some other examples of queries you can use.
            #param['q'] = "mimeType='application/vnd.google-apps.folder'"
            #param['q'] = "modifiedDate > '2016-07-12T12:00:00'"
            if page_token:
                param['pageToken'] = page_token
            files = service.files().list(**param).execute()

            result.extend(files['items'])
            page_token = files.get('nextPageToken')
            param['pageToken'] = page_token
            if not page_token:
                break
        except errors.HttpError, error:
            print('An error occurred while retrieving files in folder %s: %s' % (folder_id,error))
            break
    return result # Proof to me that python indentation requirement is stupid. I spent 2 hours trying to figure out why this
                  # this function was returning nothing only to realize that I didn't have my return statement in the 
                  # right place because I didn't notice where it was. With brackets, I would have noticed this mistake.
    #return files['items']

def walk_folders(service, folder_id):
    allfiles = []
    pp = pprint.PrettyPrinter(indent=4)

    files = get_files_in_folder(service, folder_id)
    allfiles.extend(files)
    for file_entry in files:
        file_mimetype = file_entry['mimeType']
        file_id = file_entry['id']
        if file_mimetype == 'application/vnd.google-apps.folder':
            allfiles.extend(walk_folders(service, file_id))

    return allfiles



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


        except errors.HttpError, error:
            print('An error occured: %s' % error)
            break

    result = re.sub(directory_separator + '$', '', result) # Remove directory_separator from the end of a path.

    return result


def main():
    """List all files and folders recursively under the specified folder id.
    """

    folderids = [];

	# Get the arguments for the folders to check or from the config file.
    if (len(sys.argv) > 1):
        argumentlist = sys.argv[1:]
        for folderid in argumentlist:
            folderids.append(folderid)

    else:
        for section in parser.sections(): # Fix this later.
            for name,value in parser.items(section):
                if name == "url":
                    folderids.append(value)


    pp = pprint.PrettyPrinter(indent=4)

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v2', http=http)
    numberoffiles = 0
	
    # Get our list of file IDs.
    for start_folder_id in folderids:
        #returnedfiles = get_files_in_folder(service, start_folder_id)
        returnedfiles = walk_folders(service, start_folder_id)
        #pp.pprint(returnedfiles)
        #print(type(returnedfiles))
        if type(returnedfiles) == list:
            for fileitem in returnedfiles:
                path = build_first_path(service,fileitem['id'])
                #print(fileitem['id'] + "    " + fileitem['mimeType'] + "     " + path  + fileitem['title'])
                fieldsep = u' \u2588 ' # Unicode Full block
                outputline = u"{1:<45} {0} {2:<45} {0} {3}".format(fieldsep, fileitem['id'], fileitem['mimeType'], path)
                print(outputline)
                #print(fileitem['id'] + "    " + fileitem['mimeType'] + "     " + fileitem['title'])
                numberoffiles+=1

    print("Total files: " + str(numberoffiles))

if __name__ == '__main__':
    main()
