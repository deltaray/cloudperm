import sqlite3
from sqlite3 import Error

from tkinter import *
from tkinter.messagebox import showinfo
from random import *

import csv
import json
 
############################################GUI INPUT FOR QUERIES############################################
class Application(Frame):
    
    def __init__(self, master):
        Frame.__init__(self, master)
        self.grid()
        self.create_widgets()

    def create_widgets(self):
        #query buttons 
        self.query = StringVar()
        self.query.set(None)
        Radiobutton(self, text = "Run query to determine which files the entered email address has write permissions to", variable = self.query, value ='a').grid(row = 0, column = 0, sticky = W)
        Radiobutton(self, text = "insert email to determine if the email was last used to modify any file", variable = self.query, value ='b').grid(row = 1, column = 0, sticky = W)
        Radiobutton(self, text = "use email to determine what files they are owner of any files in drive", variable = self.query, value ='c').grid(row = 2, column = 0, sticky = W)
        # Radiobutton(self, text = "files modified after certain date/time ", variable = self.query, value ='d').grid(row = 3, column = 0, sticky = W) #currently does not work 
        
        #creates label
        self.lbl = Label(self, text="Enter an email address:")
        self.lbl.grid(row =  5, column = 0, sticky = W)
        
        #creates Entry box
        self.ent = Entry(self, width = 15)
        self.ent.grid(row = 6, column = 0, sticky = W)

        #creates button / when pressed command = self.enter
        self.bttn1 = Button(self, text = "Enter", command = self.enter).grid(row = 7, column = 0, sticky = W)

        #binds keypress
        self.ent.bind('<Return>', self.enter_click)
        
        
    def enter(self):
        #gets value out of entry box
        email = self.ent.get()

        #delets enty in the box
        self.ent.delete(0, END)
        
############### queries #######################
        #db connection 
        conn = sqlite3.connect('listFiles.db')
        c = conn.cursor()
        #get email input 
        query= self.query.get()
        q = ''
        results = []
        #which query to run based on user input
        if query == 'a':
            #insert email address and return all the files that individual has role 'writer'
            #return email, name, fileID, file name, last date modified
            writer = "SELECT f.fileID, f.name, u.name, u.email FROM files AS f JOIN file_writers as w ON w.fileID == f.fileID JOIN users as u ON u.email == writer_email WHERE writer_email =?"
            c.execute(writer, [email])
            results = c.fetchall()
            q ='perm'
                
        elif query == 'b':
            #insert email to determine if the email was last used to modify any file
            #return modified datetime, email, name, fileID, file name 
            mod = "SELECT f.name, f.fileID, f.last_modifier, f.modified_time, u.name FROM files AS f JOIN users AS u on f.last_modifier = u.email WHERE f.last_modifier = ?"
            results = c.execute(mod, [email])
            results = c.fetchall()
            q = 'lat_mod'
                
        elif query == 'c':
            #use email to determine what files they are owner of
            #return file name and fileID
            #what can we do about these files in drive/permissions???? 
            owner = "SELECT f.name, f.fileID, u.name, u.email FROM files AS f JOIN users AS u on f.owner_email = u.email WHERE f.owner_email = ?"
            results = c.execute(owner, [email])
            results = c.fetchall()
            q = 'owner'
            
        elif query == 'd':
            #files modified after certain date/time 
            #return fileName, fileID, mod email, mod user name 
            #print time: YYYY-MM-DDTHH:MM:SS.nnnZ
            # mod_time = 2021-2-9
            # m_time = "SELECT f.fileID, f.name, u.name, u.email FROM files AS f JOIN file_writers as w ON w.fileID == f.fileID JOIN users as u ON u.email == w.writer_email WHERE f.modified_time >?"
            # results = c.execute(m_time, [email])
            #results = c.fetchall()
            self.lbl["text"] = "something is working"
        #if invalid input is put in     
        else:
            # if the nums aren't == then change the label to try again 
            self.lbl["text"] = "Try Again!"
        #output
        if query == 'a' or 'b' or 'c' or 'd':
            #json file 
            with open(email+'_'+q+'_results.json', 'w') as json_file:
                json.dump(results, json_file)
            with open(email+'_'+q+'_results.csv', 'w') as csv_file:
                csvwriter = csv.writer(csv_file)
                #write  to .csv
                csvwriter.writerows(results)
            #create and write TSV files   
            with open(email+'_'+q+'_results.tsv', 'w') as tsv_file:
                tsvWriter = csv.writer(tsv_file, delimiter='\t')
                #write  to .tsv
                tsvWriter.writerows(results)
            self.lbl["text"] = "Query ran on:", email, "Please check directory for outputs of query"
            
    #allows  enter/ return key to initiat the enter function to run versus just clikcing the button
    def enter_click(self, event):
        if event.keysym == "Return" or "Enter":
            self.enter()
######thoughts#######
#return search query values into a csv/tsv/json file???

# main
root = Tk()
root.title("Search Queries")
root.geometry("800x300")
root.resizable(width = TRUE, height = TRUE)

app = Application(root)
root.mainloop()
#############################################################################################################

#for database we could create new tables with different user groups-> for comparisson ie 
###team koala (name, email address)-> this will be complicated to normalize 

##blacklist email address-> send alerts if the appear in database / run in update script??

###time query 




