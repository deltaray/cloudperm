#!/usr/bin/env python3

import tkinter as tk 
from tkinter import ttk
from tkinter.messagebox import showinfo
from random import *

import csv
import json

import sqlite3
from sqlite3 import Error

from cloudperm import *
from getFiles import *
# from revokeGUI import *
# from cp_gui import *a
# from auto_revoke import *
# makDB()
class unifiedGUI(tk.Tk):
    # __init__ function for class tkinterApp 
    def __init__(self, *args, **kwargs): 
         
        # __init__ function for class Tk
        tk.Tk.__init__(self, *args, **kwargs)
         
        # creating a container
        container = tk.Frame(self)  
        container.pack(side = "top", fill = "both", expand = True) 
  
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)
  
        # initializing frames to an empty array
        self.frames = {}  
  
        # iterating through a tuple consisting
        # of the different page layouts
        for F in (StartPage, gFiles, Queries, autoRevoke, mRevoke):
  
            frame = F(container, self)
  
            # initializing frame of that object from
            # startpage, page1, page2 respectively with 
            # for loop
            self.frames[F] = frame 
  
            frame.grid(row = 0, column = 0, sticky ="nsew")
  
        self.show_frame(StartPage)
  
    # to display the current frame passed as
    # parameter
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
    makeDB()
#####################################

class StartPage(tk.Frame):
    def __init__(self, parent, controller): 
        tk.Frame.__init__(self, parent)
         
        # label of frame Layout 2
        label = ttk.Label(self, text ="Start Cloudperm")
         
        # putting the grid in its place by using
        # grid
        label.grid(row = 0, column = 4, padx = 10, pady = 10) 
  
        button1 = ttk.Button(self, text ="getFiles",
        command = lambda : controller.show_frame(gFiles))
     
        # putting the button in its place by
        # using grid
        button1.grid(row = 1, column = 1, padx = 10, pady = 10)
  
        ## button to show frame 2 with text layout2
        button2 = ttk.Button(self, text ="Queries",
        command = lambda : controller.show_frame(Queries))
     
        # putting the button in its place by
        # using grid
        button2.grid(row = 2, column = 1, padx = 10, pady = 10)
        
        ## button to show frame 2 with text layout2
        button3 = ttk.Button(self, text ="Automated Revoke",
        command = lambda : controller.show_frame(autoRevoke))
     
        # putting the button in its place by
        # using grid
        button3.grid(row = 3, column = 1, padx = 10, pady = 10)
        
        ## button to show frame 2 with text layout2
        button4 = ttk.Button(self, text ="Manual revoke",
        command = lambda : controller.show_frame(mRevoke))
     
        # putting the button in its place by
        # using grid
        button4.grid(row = 4, column = 1, padx = 10, pady = 10)
        
############################################################################
class gFiles(tk.Frame):
     
    def __init__(self, parent, controller):        
        tk.Frame.__init__(self, parent)       
        label = ttk.Label(self, text ="getFiles")
        label.grid(row = 0, column = 4, padx = 10, pady = 10)  
        button1 = ttk.Button(self, text ="Main Menu", command = lambda : controller.show_frame(StartPage))
        button1.grid(row = 1, column = 1, padx = 10, pady = 10)
        #####
        self.file = tk.StringVar()
        self.file.set(None)
        tk.Radiobutton(self, text = "Yes, I have a fileID I want to enter", variable = self.file, value ='a').grid(row = 3, column = 0, sticky = 'W')
        tk.Radiobutton(self, text = "No, run Cloudperm for all my shared files", variable = self.file, value ='b').grid(row = 4, column = 0, sticky = 'W')
        self.lbl = tk.Label(self, text="Do you have a fileID you want start the program on:")
        self.lbl.grid(row = 2, column = 0)               
        #creates Entry box
        self.lbl1 = tk.Label(self, text="Enter the fileID you want start the program on:")
        self.lbl1.grid(row =  5, column = 0)
        self.ent = tk.Entry(self, width = 20)
        self.ent.grid(row = 6, column = 0)
        
    ###############################
        #creates button / when pressed command = self.enter 
        self.bttn1 = tk.Button(self, text = "Enter", command = self.enter).grid(row = 7, column = 0)
        #binds keypress
        self.ent.bind('<Return>', self.enter_click)
        
    def enter(self):
        #gets value out of entry box
        value= self.file.get()
        start_file = self.ent.get()
        self.ent.delete(0, tk.END) 
        
        if value == 'a':
            getFiles(start_file)
        else:
            getFiles(None)
        
    def enter_click(self, event):
        if event.keysym == "Return" or "Enter":
            self.enter()  
    ######
    
############################################################################  
class Queries(tk.Frame): 
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text ="Queries")
        label.grid(row = 0, column = 4, padx = 10, pady = 10)
        
        button1 = ttk.Button(self, text ="Main Menu", command = lambda : controller.show_frame(StartPage))
        button1.grid(row = 0, column = 1, padx = 10, pady = 10)
        
    ######
        #query buttons 
        self.query = tk.StringVar()
        self.query.set(None)
        tk.Radiobutton(self, text = "Run query to determine which files the entered email address has write permissions to", variable = self.query, value ='a').grid(row = 1, column = 0, sticky = 'W')
        tk.Radiobutton(self, text = "insert email to determine if the email was last used to modify any file", variable = self.query, value ='b').grid(row = 2, column = 0, sticky = 'W')
        tk.Radiobutton(self, text = "use email to determine what files they are owner of any files in drive", variable = self.query, value ='c').grid(row = 3, column = 0, sticky = 'W')
        # tk.Radiobutton(self, text = "files modified after certain date/time ", variable = self.query, value ='d').grid(row = 3, column = 0, sticky = W) #currently does not work 
        
        #creates label
        self.lbl = tk.Label(self, text="Enter an email address:")
        self.lbl.grid(row =  5, column = 0, sticky = 'W')        
        #creates Entry box
        self.ent = tk.Entry(self, width = 25)
        self.ent.grid(row = 6, column = 0, sticky = 'W')
        #creates button / when pressed command = self.enter
        self.bttn1 = tk.Button(self, text = "Enter", command = self.enter).grid(row = 7, column = 0, sticky = 'W')
        #binds keypress
        self.ent.bind('<Return>', self.enter_click)
        
        
    def enter(self):
        #gets value out of entry box
        email = self.ent.get()

        #delets enty in the box
        self.ent.delete(0, tk.END)
        
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
    
############################################################################
class autoRevoke(tk.Frame): 
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text ="Auto Revoke")
        label.grid(row = 0, column = 4, padx = 10, pady = 10)

        button1 = ttk.Button(self, text ="Main Menu", command = lambda : controller.show_frame(StartPage))
        button1.grid(row = 1, column = 1, padx = 10, pady = 10)
        
    ############
    #creates label
        self.lbl = tk.Label(self, text="Enter the full filename with the .csv extension here:")
        self.lbl.grid(row =  2, column = 0, sticky = 'W')
        
        #creates Entry box
        self.ent = tk.Entry(self, width = 30)
        self.ent.grid(row = 3, column = 0, sticky = 'W')      
        ###############################
        #creates button / when pressed command = self.enter
        self.bttn1 = tk.Button(self, text = "Enter", command = self.enter).grid(row = 4, column = 0, sticky = 'W')

        #binds keypress
        self.ent.bind('<Return>', self.enter_click) 
        
    def enter(self):
        #gets value out of entry box
        file = self.ent.get()
        self.ent.delete(0, tk.END)
        auto_rev(file)
        #delets enty in the box
        
    def enter_click(self, event):
        if event.keysym == "Return" or "Enter":
            self.enter() 

############################################################################
class mRevoke(tk.Frame): 
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text ="Manual Revoke")
        label.grid(row = 0, column = 4, padx = 10, pady = 10)
        button1 = ttk.Button(self, text ="Main Menu", command = lambda : controller.show_frame(StartPage))
        button1.grid(row = 1, column = 1, padx = 10, pady = 10)
    
    ######
        #creates label
        self.lbl = tk.Label(self, text="Enter the email address to revoke access to:")
        self.lbl.grid(row =  2, column = 0, sticky = 'W')
        
        #creates Entry box
        self.ent = tk.Entry(self, width = 15)
        self.ent.grid(row = 3, column = 0, sticky = 'W')
        
        ###############################
        self.lbl1 = tk.Label(self, text="Enter a fileID or list of fileIDs seperated by commas:")
        self.lbl1.grid(row =  4, column = 0, sticky = 'W')
        
        #creates Entry box
        self.ent1 = tk.Entry(self, width = 50)
        self.ent1.grid(row = 5, column = 0, sticky = 'W')

        #creates button / when pressed command = self.enter
        self.bttn1 = tk.Button(self, text = "Enter", command = self.enter).grid(row = 7, column = 0, sticky = 'W')
        #binds keypress
        self.ent.bind('<Return>', self.enter_click)
        
    def enter(self):
        #gets value out of entry box
        email = self.ent.get()
        files = self.ent1.get()
        #deletes enty in the box
        self.ent.delete(0, tk.END) 
        self.ent1.delete(0, tk.END)
        m_rev(email, files)    
        
    def enter_click(self, event):
        if event.keysym == "Return" or "Enter":
            self.enter()  


############################################################################
# Driver Code
app = unifiedGUI()
app.mainloop()
###################
