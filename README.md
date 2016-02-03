# gdoc_perm_checker
An app that checks the permissions of Google Drive documents against a config file.

# GOAL

 To automate the checking of access permissions on Google Drive documents and folders and alert the user of unexpected changes.

# DEPENDENCIES

This software depends on the following python modules:

1. httplib2
2. ConfigParser
3. apiclient
4. oauth2client

# CONFIGURATION

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

 Now you will need to put a list of URLs into a config file so that the program can read that list and check the permissions
 and report them back you to.

The next part is currently optional. Eventually a config file will need to be created.
 
 Create a file called DriveConfig.INI or use the existing one and put each Google drive URL into a command separated list as
 a value of the keyword url.  Like this:
```
[urls]
url = "googledrivedocumenturl1", "googledrivedocumenturl2", etc...
```
 If you need to make comments in the document, you can do so by starting the line with a # character. The rest of such a
 line will be ignored.

# USAGE

## listFiles.py
```
listFiles.py
```

## permissionList.py
```
permissionList.py <GoogleDocumentID>
```
 
# OUTPUT

  Upon running the program, it will read the list of urls to check from the config file and print out a list
  of permissions that each user has for each document or folder. Here is an example of the program's output:
  
  ```
  $ python permissionList.py
  Document Title: My Test Document
   owner: jsmith31556@google.com
   writer: fjones55@wwjjhu.edu
   WARNING: ANYONE WITH THE LINK CAN READ THIS DOCUMENT.
  ```
  
# AUTHORS

gdoc_perm_checker was written by Mark Krenz and Shruthi Katapally
