#!/usr/bin/python

# This program revokes a specific user's access specified by their email address and the document ID.

from __future__ import print_function
import httplib2
import os
import sys

from ConfigParser import SafeConfigParser

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

from apiclient import errors

import pprint
# ...


# For whatever reason, the proper scope for revoking permissions is /auth/drive and not /auth/drive.metadata
SCOPES = 'https://www.googleapis.com/auth/drive'
APPLICATION_NAME = 'Drive API Python Quickstart'


try:
    import argparse
    parser = argparse.ArgumentParser(parents=[tools.argparser])
    parser.add_argument('revokeaccount', type=str, help='Account to revoke the permissions for the provided Document IDs')
    parser.add_argument('documents', metavar='DocumentID', type=str, nargs='+', help='Google Document IDs')
    flags = parser.parse_args()
except ImportError:
    flags = None


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

    client_secret_file = os.path.join(credential_dir, 'client_secret.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(client_secret_file, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
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
    except errors.HttpError, error:
        print ('An error occurred: %s' % error)
    return None

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
    except errors.HttpError, error:
        print ('An error occured: %s' % error)
    return None

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
    except errors.HttpError, error:
        print ('An error occured: %s' % error)
    return None


def revoke_document_role(service, file_id, role_id):
    # A non batch operation to revoke a specific permission.
    """Delete a specific permission on a permission file.

    Args:
        service: Drive API service instance.
        file_id: file ID of the file to revoke the perm for.
        role_id: permission ID of the file to retrieve the parents for
    Returns:
    Success or failure.
    """
    try:
        param = {}
        param['fileId'] = file_id
        param['permissionId'] = role_id
        # delete/revoke the permission from the document.
        returnval = service.permissions().delete(**param).execute()
        return returnval
    except errors.HttpError, error:
        print ('An error occured: %s' % error)
 
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
	
    parser = SafeConfigParser()
    parser.read("DriveConfig.INI")

    # Get our list of file IDs to check, either form the config file or from the command line arguments.

    fileids = [];

    accountToRevoke = flags.revokeaccount

    if (len(flags.documents) > 0):
        for fileid in flags.documents:
            fileids.append(fileid)
        
    else:
        for section in parser.sections(): # Fix this later.
            for name,value in parser.items(section):
                if name == "url":
                    fileids.append(value)


    for fileid in fileids:
        title = retrieve_document_title(service, fileid);
        #print("Document Title: " + title);
        perm_list = retrieve_permissions(service, fileid)
       
        accountrevoked = False;
        
        for entry in perm_list:
            if type(entry) is dict:
                if 'emailAddress' in entry:
                    #print("  " + entry['role'] + ":  " + entry['emailAddress']);
                    if entry['emailAddress'] == accountToRevoke:
                        permIdToRevoke = entry['id']
                        revoke_response = revoke_document_role(service, fileid, permIdToRevoke);

                        pp = pprint.PrettyPrinter(indent=8,depth=6)
                        #pp.pprint(entry);
                        if revoke_response:
                            pp.pprint(revoke_response);
                        else: # An empty response to 
                            accountrevoked = True;
                            print("Revoked access for " + accountToRevoke + " from document '" + title + "'");

        if not accountrevoked:
            print("WARNING: access was not revoked for " + accountToRevoke + " on file '" + title + "'");




                    	

if __name__ == '__main__':
    main()
