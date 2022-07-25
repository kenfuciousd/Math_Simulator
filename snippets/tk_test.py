# tk_test.py

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
from tkinter import *

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        #configuring root window
        self.title("tk testing app")
        self.geometry('300x500')
        self.columnconfigure(0, weight = 1)
        self.columnconfigure(2, weight = 1)
        self.columnconfigure(3, weight = 1)                
        #label
        self.label = ttk.Label(self, text='Hello, Tkinter!')
        self.label.pack
        #button
        self.button = ttk.Button(self, text='Click Me')
        self.button.grid(row = 0, column = 1)
        self.button['command']=self.button_clicked 
        #self.button.pack()
        #self.frame1 = Frame(self)
        #self.frame1.pack()
        self.label1 = tk.Label(self, text="Bet ").grid(row = 1, column = 0)
        #self.label1.pack( side = LEFT)
        self.bet_entry = tk.Entry(self, width = 8).grid(row = 0, column = 2)
        self.bet_entry.insert(0,0.25)
        #self.bet_entry.pack(padx = 15, pady = 15, side = RIGHT)
        self.frame2 = Frame(self)
        self.frame2.pack()
        self.label2 = tk.Label(self.frame2, text="Credits  ")
        self.label2.pack( side = LEFT)
        self.credit_entry = tk.Entry(self.frame2, width = 8)
        self.credit_entry.insert(0,0.25)
        self.credit_entry.pack(padx = 15, pady = 15, side = RIGHT)        
    def button_clicked(self):
        messagebox.showinfo(title='Information', message="Hello, Tkinter!")

if __name__ == "__main__":
    app = App()
    app.mainloop()