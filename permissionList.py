from __future__ import print_function
import httplib2
import os

from ConfigParser import SafeConfigParser

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

from apiclient import errors
# ...

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/drive.metadata.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
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

def main():
	"""Shows basic usage of the Google Drive API.
	
	Creates a Google Drive API service object and outputs the names and IDs
	for up to 10 files.
	"""
	credentials = get_credentials()
	http = credentials.authorize(httplib2.Http())
	service = discovery.build('drive', 'v2', http=http)
	
	parser = SafeConfigParser()
	parser.read("DriveConfig.ini")
	
	for urls in parser.sections():
		for name,value in parser.items(urls):
			id = parser.items(urls)[0][1]
			fileId = id.split("=")[1]
					
#	fileId = '1D_kVj6eZLeBYkw19G18t0fsb0DXQww-swcoWGJj_ERo'
	perm_list = retrieve_permissions(service, fileId)
	print (perm_list)
	
#    results = service.files().list(maxResults=10).execute()
#    items = results.get('items', [])
#    if not items:
#        print('No files found.')
#    else:
#        print('Files:')
#        for item in items:
#            print('{0} ({1})'.format(item['title'], item['id']))

if __name__ == '__main__':
    main()