# gdoc_perm_checker
An app that checks the permissions of Google Drive documents against a config file.

GOAL

 To automate the checking of access permissions on Google Drive documents and folders and alert the user of unexpected changes.

DEPENDENCIES

CONFIGURATION

 Before using this program, you will need to register your account with the Google API first. This is done by visiting
 https://console.developers.google.com/start/api?id=drive
 1. Sign into your account and create a new project named according to what you want to call your google drive auditing program.
 2. Select New credentials in the central window that comes up and choose OAuth clien ID
 3. You may need to configure the project name on the consent screen.
 4. Specify that this is a command line client
 5. Once it shows you the client id credentials you can click ok and then download the json file with the client credentials.
 6. Put the json file you downloaded into the project folder along with the program. Name it client_secret.json

 Next, you will need to authenticate the software with your Google account. You do this by first logging into
 your Google account in your web browser. Then you run the program as shown below. The program will open up an authentication
 link in your browser and ask you to accept the access by the program.

USAGE

 python permissionList.py
 
 
OUTPUT

  Upon running the program, it will read the list of urls to check from the config file and print out a list
  of permissions that each user has for each document or folder.
  
  
