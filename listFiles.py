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
    result = []
    page_token = None

    while True:
        try:
            param = {}
            #param['maxResults'] = 1000
            param['maxResults'] = 1000
            if page_token:
                param['pageToken'] = page_token
            files = service.files().list(**param).execute()

            result.extend(files['items'])
            page_token = files.get('nextPageToken')
            if not page_token:
                break
        except errors.HttpError, error:
            print('An error occurred: %s' % error)
            break
        return result

def build_first_path(service, file_id):
    """Build the full path of the first parent in the list of parents
    """
    result = "" 
    isroot = 0;

    while isroot == 0:
        try:
            thefile = service.files().get(fileId=file_id).execute()
            #print("path is now " + result)
            #print("looking at " + thefile['title'])
            if len(thefile['parents']) == 0:
                #print("This document was shared with you, but not part of your my drive")
                result = "[SHARED WITH YOU]/" + result
                break
            else:
                parentfile = thefile['parents'][0] # Let's just use the first one for now. We'll handle multiple later.
            #print("parents: " + str(parentfile))
            if parentfile['isRoot'] == True:
                isroot = 1;
                #print("Found the root")
                result = "/" + thefile['title'] + "/" + result
                #print("Final result was " + result)
                break
            else:
                #print("Going up a dir to " + parentfile['id'])
                result = thefile['title'] + "/" + result
                file_id = parentfile['id']


        except errors.HttpError, error:
            print('An error occured: %s' % error)
            break

    result = re.sub('/$', '', result)
    result

    return result



def main():
    """Shows basic usage of the Google Drive API.

    Creates a Google Drive API service object and outputs the names and IDs
    for up to 10 files.
    """

    pp = pprint.PrettyPrinter(indent=4)

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v2', http=http)
	

    # Get our list of file IDs.


    allfiles = retrieve_all_files(service)
    numberoffiles = len(allfiles);
    print("Total files: " + str(numberoffiles))
    for fileitem in allfiles:
        path = build_first_path(service,fileitem['id'])
        print(fileitem['id'] + "    " + fileitem['mimeType'] + "     " + path) # + fileitem['title'])
	

if __name__ == '__main__':
    main()
