#!/usr/bin/env python3

from tkinter import *
from tkinter.messagebox import showinfo
from random import *

from cp import * 

class enterFile(Frame):  
    def __init__(self, master):
        Frame.__init__(self, master)
        self.grid()
        self.create_widgets()

    def create_widgets(self):
        #creates label
        self.file = StringVar()
        self.file.set(None)
        Radiobutton(self, text = "Yes, I have a fileID I want to enter", variable = self.file, value ='a').grid(row = 1, column = 0, sticky = W)
        Radiobutton(self, text = "No, run Cloudperm for all my shared files", variable = self.file, value ='b').grid(row = 2, column = 0, sticky = W)
        self.lbl = Label(self, text="Do you have a fileID you want start the program on:")
        self.lbl.grid(row =  0, column = 0, sticky = W)
        
        #creates Entry box
        self.lbl1 = Label(self, text="Enter the fileID you want start the program on:")
        self.lbl1.grid(row =  4, column = 0, sticky = W)
        self.ent = Entry(self, width = 20)
        self.ent.grid(row = 5, column = 0, sticky = W)
        
        ###############################
        #creates button / when pressed command = self.enter 
        self.bttn1 = Button(self, text = "Enter", command = self.enter).grid(row = 6, column = 0)
        #binds keypress
        self.ent.bind('<Return>', self.enter_click)
          
    def enter(self):
        #gets value out of entry box
        value= self.file.get()
        start_file = self.ent.get()
        self.ent.delete(0, END) 
        
        if value == 'a':
            listFiles(start_file)
        else:
            listFiles()
        
    def enter_click(self, event):
        if event.keysym == "Return" or "Enter":
            self.enter()  
        
#main
root = Tk()
root.title("Start Cloudperm by insering you data here")
root.geometry("800x300")
root.resizable(width = TRUE, height = TRUE)
app = enterFile(root)
root.mainloop()