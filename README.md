# Cloudperm
A set of programs that help you check, audit report and change roles and permissions on popular Cloud platforms.
Right now this is only for Google Drive/Docs.

# GOAL

 To automate the checking of access permissions on cloud file/document sharing platforms such as Google Drive and alert the user of unexpected changes.

# DEPENDENCIES

This software depends on the following python modules:

1. httplib2
2. ConfigParser
3. (https://github.com/googleapis/google-api-python-client)
4. oauth2client
5. future
6. pyDAL
7. mysql 
Depending on your distribution, you may need to install other modules to meet the above
depencies.

# CONFIGURATION

 NOTE: The steps below may vary a bit from what you end up seeing due to changes in Google's registration
 process or the unique qualities or state of your own account. You may need to look around a bit to find
 the correct location to complete a step in this process.
 
 Before using this program, you will need to register your account with the Google API first. This is done by first visiting
 https://console.developers.google.com/start/api?id=drive
 1. Sign into your account and create a new project named according to what you want to call your google drive auditing program.
 2. Select New credentials in the central window that comes up and choose OAuth client ID
 3. You may need to configure the project name on the consent screen.
 4. Specify that this is a command line client
 5. Once it shows you the client id credentials you can click ok and then download the json file with the client credentials.
 6. Put the json file you downloaded into the project folder along with the program. Name it client_secret.json

 Next, you will need to authenticate the software with your Google account. You do this by first logging into
 your Google account in your web browser. Then you run the 'listFiles' program, which upon first run will try to
 complete the initial oauth setup process. The program will open up an authentication link in your browser
 and ask you to accept the access by the program.

```
./listFiles
```

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

## listFiles
```
listFiles [Google Folder DocumentID] [Folder DocID 2] [...]
```
listFiles can either be run without an argument to show the files and folders under your My Drive section, or
by specifying one more more folder document ids, the sub files and folders of those folders. You can also
recursively decend into subfolders with the --recursive option and specify a maximum depth to decend with
--max-depth. If you want to exclude specific subfolders you can do that by using one or more
--exclude-folder options.

Example: 
```
listFiles --recursive --max-depth 3 -E d9da230885ad407bb0461f6e37979208 -E c4905df255834c338cd9bdddb4f8321c 4bdff3cd0926432c94c2d90be7f3890b | tee drivefiles.txt
```
This will recursively walk the folder "heirarchy starting with the folder with docid 4bdff3cd0926432c94c2d90be7f3890b
and it will not decend into the folders with document ids d9da230885ad407bb0461f6e37979208 or c4905df255834c338cd9bdddb4f8321c. 
It will then pass the output to the tee program, writing to the file 'drivefiles.txt' while also displaying a copy
of the data in the terminal.

Note, it can take a non-trivial amount of time before starts displaying output and may take a while to completely finish.


## permissionList
```
permissionList <Google DocumentID>
```
 
# OUTPUT

  Upon running the program, it will read the list of urls to check from the config file and print out a list
  of permissions that each user has for each document or folder. Here is an example of the program's output:
  
  ```
  $ permissionList 9F0A44B460A94E0281A8604A0EFE1C96
  Document Title: My Test Document
   owner: jsmith31556@google.com
   writer: fjones55@wwjjhu.edu
   WARNING: ANYONE WITH THE LINK CAN READ THIS DOCUMENT.
  ```

# WORKFLOW

This software has been designed so that you utilize the different commands as part of an overall workflow as follows:

* listFiles -r '''folder docid'''
* permissionList '''docid'''
* As needed: revokeAccess '''accountemail''' '''docid'''
* [Wash and repeat]

All these programs can take more than one document id as an argument and process the list. It is up
to you, however the author of the software usually runs the programs in this fashion.

* listFiles -r C9A6BD209F8A4F02A019D2DA09725D57 | tee drive-files-YYYYMMDD.txt
* cat drive-files-YYYYMMDD.txt | while read docid undef ; do permisssionList "$docid" ;echo ; done | tee drive-files-perms-YYYYMMDD.txt
* grep -e "Doc Id:" -e "Path:" -e WARNING drive-files-perms-YYYYMMDD.txt | grep -B2 WARNING | less -S


 
  
# AUTHORS

cloudperm was written by Mark Krenz and Matt Brownlee and is released under a GPL version 2 license.
Some initial work on this project was also by Shruthi Katapally.
