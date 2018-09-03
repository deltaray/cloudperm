
import httplib2
import os
import sys

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

from apiclient import errors

from ConfigParser import SafeConfigParser

import pprint



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
    credential_path = os.path.join(credential_dir, 'drive-python-quickstart.json')
    client_secret_file = os.path.join(credential_dir, 'client_secret.json');

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


