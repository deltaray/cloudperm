
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


def walk_folders(service, folder_id, depth=0):
    allfiles = []
    pp = pprint.PrettyPrinter(indent=4)

    files = get_files_in_folder(service, folder_id)
    allfiles.extend(files)
    for file_entry in files:
        file_mimetype = file_entry['mimeType']
        fild_id = file_entry['id']
        if file_mimetype == 'application/vnd.google-apps.folder' and depth > 0:
            allfiles.extend(walk_folders(service, fild_id, --depth))

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

    result = re.sub('/$', '', result)

    return result

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
    except errors.HttpError, error:
        print ('An error occured: %s' % error)


