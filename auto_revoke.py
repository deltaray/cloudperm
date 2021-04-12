#!/usr/bin/env python3

from cloudperm import *
import csv 
from tkinter import *
from tkinter.messagebox import showinfo
from random import *


import argparse
parser = argparse.ArgumentParser(parents=[cloudperm_argparser])
args = parser.parse_args()

credentials = get_credentials(args)
http = credentials.authorize(httplib2.Http())
service = discovery.build('drive', 'v2', http=http)



def auto_rev(file):    
    #list to make list of list   
    rows =[]
    
    #read csv in 
    with open(file, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        
        #make list of lists 
        for row in csvreader:
            rows.append(row)
            
        #get data from list of lists
        for item in rows:
            email= item[3]
            fileid = item[0]
            
            #revoke access 
            title = retrieve_document_title(service, fileid);
            # print("TITLE", title)
            perm_list = retrieve_permissions(service, fileid)
            accountrevoked = False;
            
            for entry in perm_list:
                # print("permlist", perm_list)
                if type(entry) is dict:
                    if 'emailAddress' in entry:
                        if entry['emailAddress'] == accountToRevoke:
                            permIdToRevoke = entry['id']
                            revoke_response = revoke_document_role(service, fileid, permIdToRevoke);

                            pp = pprint.PrettyPrinter(indent=8,depth=6)
                            if revoke_response:
                                pp.pprint(revoke_response);
                            else: # An empty response to 
                                accountrevoked = True;
                                # print("Revoked access for " + accountToRevoke + " from document '" + title + "'");
                                print("Access has successfully wbeen revoked for", email, "on", fileid)

            if not accountrevoked:
                # print("WARNING: access was not revoked for " + accountToRevoke + " on file '" + title.encode('utf-8') + "'");ess was not revoked for " + accountToRevoke + " on file '" + title.encode('utf-8') + "'");
                print("ACCOUNT WAS UNABLE TO BE REVOKED")


class Application(Frame):  
    def __init__(self, master):
        Frame.__init__(self, master)
        self.grid()
        self.create_widgets()

    def create_widgets(self):
        #creates label
        self.lbl = Label(self, text="Enter the full filename with the .csv extension here:")
        self.lbl.grid(row =  1, column = 0, sticky = W)
        
        #creates Entry box
        self.ent = Entry(self, width = 30)
        self.ent.grid(row = 2, column = 0, sticky = W)
        
        ###############################
        #creates button / when pressed command = self.enter
        self.bttn1 = Button(self, text = "Enter", command = self.enter).grid(row = 7, column = 0, sticky = W)

        #binds keypress
        self.ent.bind('<Return>', self.enter_click)
        
        
    def enter(self):
        #gets value out of entry box
        file = self.ent.get()
        self.ent.delete(0, END)
        auto_rev(file)
        #delets enty in the box
        
    def enter_click(self, event):
        if event.keysym == "Return" or "Enter":
            self.enter()          
            
#main
root = Tk()
root.title("Revoke Access-Automated")
root.geometry("800x300")
root.resizable(width = TRUE, height = TRUE)
app = Application(root)
root.mainloop()