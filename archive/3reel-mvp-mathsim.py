# mathsim.py
# 
# requirements: 
#   input: excel file with three sheets: 'Reels', "Paytable", ""Paylines"
#        Reels should have "Reel label" in row 1, and then each reel should have a set of symbols simulating the reel strip
#            each line should have only a one symbol abbreviation, reflected in the paytable
#        Paytable should have a "Reel label" in row 1, then each row should be a winning combonation
#        Paylines should have each payline with a parenthesis set of numbers, (reel,game-window-position), starting from zero. 
#            like: (0,1) | (1,2) | (2,1) which would look like a downward pointing arrow shape from the second row - _ -
# 
# python packages installed: openpyxl, tkinter

import sys
import os
import os.path
import random
import numpy as np        # random number generator, rounding
import pandas as pd     # for reading Excel
import matplotlib.pyplot as plt  # for displaying math 
import tkinter as tk    # for the gui
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
from tkinter import *
from tkinter import filedialog as fd
from collections import defaultdict
#import pygame

### slot machine class
class SlotMachine: 
    """Slot machine class, takes in the 'input' file as well as the reel # configured """ 
    # initialize, setting allowances to settings:
    def __init__(self, filepath, reels, paylines, bet, initial_credits):
        self.input_filepath = filepath
        print(f"{self.input_filepath} .. was saved from {filepath}")
        self.game_credits = initial_credits 
        self.bet = bet
        #initialize data to be used in the local object namespace, so it's able to be referenced. 
        self.game_window = []
        self.paytable = []
        self.reel1pos=0    # to edit from here into reel function
        self.reel2pos=0
        self.reel3pos=0
        self.reel1=[]
        self.reel2=[]
        self.reel3=[]
        self.wildsymbols = []
        self.paylines = []

        # if there is a file at the spot, read it. ... this logic should probably be changed/added to the payline/paytable pieces..
        try:
            reel_data = pd.read_excel(self.input_filepath, sheet_name='Reels')
            #we should set this around here... 
            self.reels = reels
            self.paylines_total = paylines            
            self.reel1 = reel_data['Reel 1']
            self.reel2 = reel_data['Reel 2']
            self.reel3 = reel_data['Reel 3']
        except:
            print(f"not a good filename: {self.input_filepath}")
        # dataframe_var.shape to get dimensionality: (22,5)    .. so dataframe_var.shape[0] is the rows (depth) and [1] is the columns (width)
        ### the reels, here, are the reel strips. 

        # chooses the random positions for each of the reels, eventually add the total reel number to pass
        self.randomize_reels()

        # load paytables
        paytable_data = pd.read_excel(self.input_filepath, sheet_name='Paytable3')
        # this is where we will call the paytable loader with the data
        self.build_paylines()

        # load reel window, paylines 
        payline_data = pd.read_excel(self.input_filepath, sheet_name='Paylines9')
        self.build_pay_table()

        if(reels == 3):
            #print("in initialize: three reels")
            # create virtual window:    (making up unused symbols to track values for deveopment) - also, setting the initial array depth to avoid index errors
            self.game_window = [['gh1', 'gh4', 'gh7'], ['gh2', 'gh5', 'gh8'], ['gh3', 'gh6', 'gh9']]
            # meaning it's called like game_window[reel][row]
            self.build_game_window(self.reel1pos, self.reel2pos, self.reel3pos)
        elif(reels == 5):
            self.game_window = [['gh1', 'gh6', 'gh11', 'gh16', 'gh21'], ['gh2', 'gh7', 'gh12', 'gh17', 'gh22'], ['gh3', 'gh8', 'gh13', 'gh18', 'gh23'], ['gh4', 'gh9', 'gh14', 'gh19', 'gh24'], ['gh5', 'gh10', 'gh15', 'gh20', 'gh25']]
            #build_game_window(reel_pos_all)
        else:
            #output logging goes here. 
            print("Check settings. Choose 3 or 5 reels.")
            quit()
        #end initialization

    def randomize_reels(self):
        #print("before randomize: " + str(self.reel1pos) + " " + str(self.reel2pos) + " " + str(self.reel3pos))
        self.reel1pos=random.randint(0,len(self.reel1)-1)
        self.reel2pos=random.randint(0,len(self.reel2)-1)
        self.reel3pos=random.randint(0,len(self.reel3)-1)
        # need to add 5 reel logic to the game window stuff later... going to leave this here as a reminder
        #if(reels==5):
        #    reelpos4=random.randint(0,len(reel4)-1)
        #    reelpos5=random.randint(0,len(reel5)-1)
        #print("after randomization, reel positions: " + str(self.reel1pos) + " " + str(self.reel2pos) + " " + str(self.reel3pos))

    def adjust_credits(self,value):
         # bets should be negative values, wins or deposits positive
        #print("Adjusting credits at " + str(value))
        self.game_credits = np.round(float(self.game_credits) + value, 2)
        #print("Adjusting credits, now: " + str(self.game_credits))

    def return_credits(self):
         return self.game_credits

    def reset_wildsymbols(self):
        """this function is used to reset the wildsymbols list, to assist the 'is_a_win' function, so that "any bars" or "any 7s", etc, don't get 'stuck' in the test """
        self.wildsymbols = ['W']
        #print("resetting wildsymbols: " + str(self.wildsymbols))

    # note will need to change these inputs, to allow for >3
    def build_game_window(self, reel1pos, reel2pos, reel3pos):
        #for now: 3 reels, more logic later - like sending a list of the positions, so it's size agnostic. 
        #     sets the window positions (reminder, game_window[row][reel])
        #if reel1 pos == 0 (or reel's 2 or three), then set (game_window[reel][0]) as reelN[len(reel1)-1)
        # else use reelN[reelposN-1]
        #print(str(reel1pos) + " " + str(reel2pos) + " " + str(reel3pos) + " " + str(len(self.reel1)-1) + " " + str(self.reel1[len(self.reel1)-1]))
        if(self.reel1pos==0):
            self.game_window[0][0]=self.reel1[len(self.reel1)-1]
        else:
            self.game_window[0][0]=self.reel1[self.reel1pos-1]
        if(self.reel2pos==0):
            self.game_window[1][0]=self.reel2[len(self.reel2)-1]
        else:
            self.game_window[1][0]=self.reel2[self.reel2pos-1]
        if(self.reel3pos==0):
            self.game_window[2][0]=self.reel3[len(self.reel3)-1]
        else:
            self.game_window[2][0]=self.reel3[self.reel3pos-1]             
        #the middle row is always true
        self.game_window[0][1] = self.reel1[self.reel1pos]
        self.game_window[1][1] = self.reel2[self.reel2pos]
        self.game_window[2][1] = self.reel3[self.reel3pos]
        #if self.reel1 pos == len(self.reel1)-1 (or self.reel's 2 or three), then set (self.game_window[self.reel][2]) as self.reelN[0]
        # else use self.reelN[self.reelposN+1]
        if(self.reel1pos==len(self.reel1)-1):
            self.game_window[0][2]=self.reel1[0]
        else:
            self.game_window[0][2]=self.reel1[self.reel1pos+1] 
        if(self.reel2pos==len(self.reel2)-1):
            self.game_window[1][2]=self.reel2[0]
        else:
            self.game_window[1][2]=self.reel2[self.reel2pos+1] 
        if(self.reel3pos==len(self.reel3)-1):
            self.game_window[2][2]=self.reel3[0]
        else:
            self.game_window[2][2]=self.reel3[self.reel3pos+1]
        ##handling for reels 4 and 5 could be here, when configured. If reels==5, do the same thing as above for all three positions, but for 5x5
        #print(self.game_window)

    def build_pay_table(self):
        #to replace with loading it in...  so in excel, 4 columns, reelNum text fields followed by the win amount
        #accessible in object with:  paytable[each_win_line from 0 to len-1][0 to len-1 for each symbol and the value]
        ##
        #### last value should be credits, to multiply vs the bet.. not dollar values
        self.paytable = [
            ('W','W','W',12.5),
            ('B7','B7','B7',11.25),
            ('R7','R7','R7',10.75),
            ('*7','*7','*7',10),
            ('3B','3B','3B',6.50),
            ('2B','2B','2B',6),
            ('1B','1B','1B',5.5),
            ('*B','*B','*B',3)
        ]
        #self.paytable = [
        #    ('W','W','W',25),
        #    ('B7','B7','B7',23),
        #    ('R7','R7','R7',22.5),
        #    ('*7','*7','*7',22),
        #    ('3B','3B','3B',5),
        #    ('2B','2B','2B',4.5),
        #    ('1B','1B','1B',4),
        #    ('*B','*B','*B',3.25)
        #]        
        # determine baseline wilds, which will always apply when encounterd
        self.wildsymbols = ['W']

    def build_paylines(self):
        #first payline: middle line; the 'reel positions'
        #paylines=[(0,1),(1,1),(2,1)]

        # this is what should be loaded from the excel sheet later
        #referenced by paylines[full-payline][payline-item-number][either 0 for reel, or 1 for position]
        #so paylines[0][2] is the third reel position to check at game_window[2][0], [2]reel three, [0]top position.
        self.paylines=[
            [(0,0),(1,0),(2,0)],
            [(0,1),(1,1),(2,1)],
            [(0,2),(1,2),(2,2)],
            [(0,0),(1,1),(2,2)],
            [(0,2),(1,1),(2,0)],
            [(0,0),(1,1),(2,0)],
            [(0,1),(1,2),(2,1)],
            [(0,1),(1,0),(2,1)],
            [(0,2),(1,1),(2,2)]
        ]

    # call win determination (send each specified payline's values to check against the paytable, #operations are paylines times paytable rows)
        # did they win? 
        # this should cycle the payline list, (each line pulling the 3 coordinates) 
        # then testing each of those against each paytable line
        # ... with special consideration for wilds, denoted *
    def is_a_win(self):
        #check payline from the reels, sending over the gamewindow array
        # so..  for each payline, grab the symbols from the game window compare to the whole paytable win list 
        #if it matches one of those lines (wild logic here), then pull the len-1 entry for that line
        iteration = 0
        for line in self.paylines:
            symbols=[]
            winbreak = 0
            iteration += 1
            for reel_pos in line:
                symbols.append(self.game_window[reel_pos[0]][reel_pos[1]])
            print(f"    testing payline {iteration} with symbols: {str(symbols)}")  # this is pulling game window correctly
            #test against paytable
            self.reset_wildsymbols()
            for payline in self.paytable:
                for reelnum in range(0, self.reels):
                    # reworking logic..
                    #print(" - testing reel: " + str(reelnum+1) + " for " + str(symbols[reelnum]) + " versus " + str(payline[reelnum]))
                    if "*" in str(payline[reelnum]):
                        #print("Found an Any Type Symbol")
                        if payline[reelnum] == '*B':
                            for sym in ['B7', '1B','2B', '3B']:
                            # eventually, logic to include the right ones from the reel.
                                self.wildsymbols.append(sym)
                            #print(" - appended Bars")
                        elif payline[reelnum] == '*7':
                            for sym in ['B7','R7']:
                                self.wildsymbols.append(sym)
                            #print(" - appended 7s")

                    # win logic                     ### NOTE: Winning logic is *HERE* 
                    if((symbols[reelnum] == payline[reelnum]) or (symbols[reelnum] in self.wildsymbols)):
                        #if they do not match at any time, return false 
                        print("        Match: " + symbols[reelnum]  + " vs " + payline[reelnum] + " on reelnum: " + str(reelnum+1)) # + " and testing reels: " + str(self.reels))
                        #payout is the last entry on the payline
                        if(reelnum + 1 == self.reels):
                            self.reset_wildsymbols()
                            print("WIN! winning: " + str(payline[len(payline)-1]) + " credits, and the payline: " + str(symbols))
                            self.adjust_credits(payline[len(payline)-1])  ### this should use credits, so bet value x the payline amount
                            winbreak = 1
                            #return True
                    else:
                        self.reset_wildsymbols()
                        break
                        #else, if it's the last reel, and it didn't match, 
                ##### double check above
                # this is to not give double rewards to the same line - in python, the test is nested, and break doesn't work inside of it due to logic. 
                if(winbreak == 1):
                    winbreak = 0
                    break

    # spin reels: a major part of the functionality 
    def spin_reels(self):
        #print("bet is " + str(self.bet) + " and paylines is " + str(self.paylines_total))
        total_bet = self.bet * float(self.paylines_total)
        #print("checking credits: " + self.game_credits + " < " + str(total_bet))
        #print("betting: " + str(total_bet*-1))
        self.adjust_credits(total_bet * -1)
        #STUB: remove wallet value: bet x paylines; check to see if player has enough
        #randomly choose reel positions for each of the reels
        self.randomize_reels()
        self.build_game_window(self.reel1pos, self.reel2pos, self.reel3pos)
        self.is_a_win()


class Simulator():
    """ simulator class: takes in the SlotMachine class object, does stuff and tracks it. """
    def __init__(self, sm, simnum):
        self.simnum = simnum
        self.sm = sm
        self.this_bet = sm.bet * float(sm.paylines_total)
        self.incremental_credits = []
        self.spins = []
        self.df_dict = ["credits"] # takes up the header line and lets us start at iteration 1 for data purposes
        self.run_sim()
        #self.plot_result()   # the automatic plotting was causing issues with things hanging until it closed. 

    def run_sim(self):
        for iteration in range(self.simnum):
            #print("spinning")
            if( self.this_bet > float(self.sm.game_credits) ):
                # can't really send back a status to the gui?? 
                #simgui.slot_check.set("[Reset Slot]")
                print("Not enough credits, $" + str(self.this_bet) + " is required.")
                break
            else:
                # some of the busy parts of the simulator. spin the slotmachine(sm)'s reels and track the data
                # choosing a dictionary for the df_dict var because it's easy to convert to a DataFrame later. 
                print(f"spin {str(iteration+1)} and credits ${str(self.sm.return_credits())}")
                self.sm.spin_reels()
                self.incremental_credits.append(self.sm.return_credits())
                self.spins.append(iteration+1)
                self.df_dict.insert(iteration+1, self.sm.return_credits())
                #print(f"spin {str(iteration)} and credits ${str(self.sm.return_credits())} and added to the dictionary: {self.df_dict[iteration]}")

    def plot_result(self):
        #plt.style.use('_mpl-gallery')
        plt.ylabel('Credits')
        plt.xlabel('Spins')
        plt.xlim(-1,self.simnum) # show total expected spins. 
        plt.plot(self.spins, self.incremental_credits)
        plt.show()

    # this should be used, in some form.. I don't like addressing this directly. However 
    #def return_dataframe(self):
    #    print(f" ... looking at {str(self.df_dict)}")
    #    return pd.DataFrame(self.df_dict)

class tkGui(tk.Tk):

    def __init__(self):
        super().__init__()  #the super is a bit unnecessary, as there is nothing to inherit... but leaving it here for reference. 
        self.debug_level = 0
        #initial gui settings and layout
        self.geometry("500x500")
        self.title("Slot Simulator")
        self.columnconfigure(0, weight = 1)
        self.columnconfigure(1, weight = 1)
        self.columnconfigure(2, weight = 1)

        # default text/value entries
        self.reel_total = IntVar(self, value = 3)   #reels would be set here? --- this should probably be done in the lot machine, after the read
        self.paylines_total = IntVar(self, value = 9) # this should also be moved to within the slot machine
        self.bet = StringVar(self, value = "0.25")  ## so I need to set this as a string in order to get a decimal.
        self.slot_ready = False
        # .. simulator settings: 
        self.initial_credits = IntVar(self, value = 100)
        self.simruns = IntVar(self, value = 500)
        self.input_filepath = StringVar(self, value = "./assets/PARishSheets.xlsx") 
        self.sim_output_filepath = StringVar(self, value = "./assets/simdata.csv")
        self.math_output_filepath = StringVar(self, value = "./assets/mathdata.csv")
        self.status_box = StringVar(self, value = "[Select Input File, then Click 1.]")
        #simulator spins/credits data
        self.df = pd.DataFrame()
        #dictionary with math, next? 
        #finally, create the gui itself, calling the function
        self.create_gui()

    #output buttons - decided to make them separate in case we want to do different things with them
    ##### currently broken.. when using .get() .. meaning it's breaking out of the text box string format...
    def input_filepath_dialog_button(self): 
        #clear out the old entries, then reset. 
        print(f"input was {self.input_filepath.get()}")  
        self.input_filepath.set("")
        self.input_file_entry.select_clear()     
        # clearing out the variables, don't work 
        the_input = fd.askopenfilename(initialdir=os.curdir, title="Select A File", filetypes=(("excel files","*.xlsx"), ("all files","*.*")) )
        self.input_filepath.set(the_input)
        print(f"input is {self.input_filepath.get()}")
        self.input_file_entry.textvariable=self.input_filepath.get()
        print(f"and the entry is {self.input_file_entry.get()}")

    def sim_output_filepath_dialog_button(self): 
        self.sim_output_filepath.set(fd.askopenfilename(initialdir=os.curdir, title="Select A File", filetypes=(("csv files","*.csv"), ("all files","*.*")) ) )
        #print(f"input is {self.sim_output_filepath}")       
        self.sim_output_file_entry.textvariable=self.sim_output_filepath.get()

    def math_output_filepath_dialog_button(self): 
        self.math_output_filepath.set(fd.askopenfilename(initialdir=os.curdir, title="Select A File", filetypes=(("csv files","*.csv"), ("all files","*.*")) ) )
        #print(f"input is {self.math_output_filepath}")
        self.math_output_file_entry.textvariable=self.math_output_filepath.get()

    def sim_output_save_file(self):
        #header = ['spin','credits']
        data = self.df
        #print(data)
        # if file does not exist, create first.. then append
        #print(self.sim_output_filepath.get())
        if(os.path.exists(str(self.sim_output_filepath)) == False):
            with open(str(self.sim_output_filepath.get()), 'w') as fp:
                fp.close()
        data.to_csv(str(self.sim_output_filepath.get()))
        print(f"saving... {str(self.sim_output_filepath.get())}")

    def math_output_save_file(self):
        data = self.df #### this will be a different data set.....
        #print(data)
        # if file does not exist, create first.. then append
        #print(str(self.math_output_filepath.get()))
        if(os.path.exists(str(self.math_output_filepath)) == False):
            with open(str(self.math_output_filepath.get()), 'w') as fp:
                fp.close()
        data.to_csv(str(self.math_output_filepath.get()))
        print(f"saving... {str(self.math_output_filepath.get())}")

    #### This is where the magic happens in the GUI, part 1
    def build_slot_button(self):
        # use the current values
        input_filepath = self.input_filepath.get() #this didnt like .get()
        #print(f" after build slot, input filepath clicked is: {input_filepath}")
        reel_total = self.reel_total.get()
        paylines_total = self.paylines_total.get()
        bet = float(self.bet_entry.get())
        initial_credits = self.credit_entry.get()
        #print(f"{filepath}, {reel_total}, {paylines_total}, {bet}, {initial_credits}")
        self.sm = SlotMachine(input_filepath, reel_total, paylines_total, bet, initial_credits) ### TODO: get reels and paylines out of it. read within the filepath
        self.slot_ready = True
        self.status_box.set("[2. Slot Built - Credits Loaded]")
        # a gui checkbox to show it was done? in the build column in slot 0?

    #### This is where the magic happens in the GUI, part 2
    def sim_button_clicked(self):
        #start simulation here...
        #print("buttonpress")
        if(self.slot_ready == True):
            self.status_box.set("[3. Done - Click 1 to Rebuild Slot]")            
            self.sim = Simulator(self.sm, self.simruns.get())   ### why isn't this able to be touched? 
            self.df = pd.DataFrame(self.sim.df_dict)
            #print(f" So here is what is returned from the SIM: \n {str(self.df)}")
        else:
            self.status_box.set("[->1. Click 1 to Build or reload]")
            #print("->1. Slot needs to be loaded first.")

    def plot_button_clicked(self):
        self.sim.plot_result()

    def create_gui(self):
        # UI element values
        gui_row_iteration = 0
        #self.input_filepath = StringVar(self, value = '/Users/jdyer/Documents/GitHub/JD-Programming-examples/Python/math_slot_simulator/PARishSheets.xlsx')
        self.label_plot = tk.Label(self, text="1. Select Input File")
        self.label_plot.grid(row = gui_row_iteration, column = 0, columnspan = 3)
        gui_row_iteration += 1
        self.input_label_filepath = tk.Label(self, text="Input Filepath ")
        self.input_label_filepath.grid(row = gui_row_iteration, column = 0)
        #self.label_filepath.pack( side = LEFT)
        self.input_file_entry = ttk.Entry(self, textvariable = self.input_filepath, text=self.input_filepath)
        #self.input_file_entry.insert(0,self.input_filepath)
        self.input_file_entry.grid(row = gui_row_iteration, column = 1)
        self.file_button = tk.Button(self, text="1. ...", command = self.input_filepath_dialog_button)
        self.file_button['command'] = self.input_filepath_dialog_button
        self.file_button.grid(row = gui_row_iteration, column = 2)
        gui_row_iteration += 1
        
        #button entries
        self.label_bet = tk.Label(self, text="Bet ")
        self.label_bet.grid(row = gui_row_iteration, column = 0, columnspan=2)
        self.bet_entry = ttk.Entry(self, width = 8, textvariable = self.bet)
        self.bet_entry.grid(row = gui_row_iteration, column = 2)
        gui_row_iteration += 1
        self.label_cred = tk.Label(self, text="Starting Dollars ")
        self.label_cred.grid(row = gui_row_iteration, column = 0, columnspan=2)
        self.credit_entry = ttk.Entry(self, width = 8, textvariable = self.initial_credits)
        self.credit_entry.grid(row = gui_row_iteration, column = 2)
        gui_row_iteration += 1

        # the status box. intentionally making it a bit obnoxious to catch the eye and because I want to change how this works later. 
        self.status_box_box = tk.Label(self, textvariable=self.status_box, bg = "dodgerblue1", fg = "ghostwhite")
        self.status_box_box.grid(row = gui_row_iteration, column = 1)
        gui_row_iteration += 1

        # build slot button
        self.label_build_slot = tk.Label(self, text="2. Build Virtual Slot ")
        self.label_build_slot.grid(row = gui_row_iteration, column = 0, columnspan = 3)
        gui_row_iteration += 1
        self.run_slots_button = tk.Button(self, text="2. Build Virtual Slot", command = self.build_slot_button)
        self.run_slots_button.grid(row = gui_row_iteration, column = 1)
        gui_row_iteration += 1
        # simulator info
        self.label_simruns = tk.Label(self, text="Simulator Total Spins" )
        self.label_simruns .grid(row = gui_row_iteration, column = 0, columnspan=2)
        self.simrun_entry = ttk.Entry(self, width = 10, textvariable = self.simruns)
        self.simrun_entry.grid(row = gui_row_iteration, column = 2)
        gui_row_iteration += 1

        # Run Button
        self.label_sim = tk.Label(self, text="3. Run Simulation")
        self.label_sim.grid(row = gui_row_iteration, column = 0, columnspan = 3)
        gui_row_iteration += 1
        self.run_sim_button = tk.Button(self, text="3. Run Simulation", command = self.sim_button_clicked)       
        self.run_sim_button.grid(row = gui_row_iteration, column = 1)
        gui_row_iteration += 1

        #sim label
        self.label_output = tk.Label(self, text="4a. Save Outputs")
        self.label_output.grid(row = gui_row_iteration, column = 0, columnspan = 3)
        gui_row_iteration += 1
        #Sim output file
        self.sim_output_label_filepath = tk.Label(self, text="Sim Output Filepath ")
        self.sim_output_label_filepath.grid(row = gui_row_iteration, column = 0)
        self.sim_output_file_entry = ttk.Entry(self, textvariable = self.sim_output_filepath, text=self.sim_output_filepath)
        self.sim_output_file_entry.grid(row = gui_row_iteration, column = 1)
        self.sim_output_file_button = tk.Button(self, text="...", command = self.sim_output_filepath_dialog_button)
        self.sim_output_file_button['command'] = self.sim_output_filepath_dialog_button
        self.sim_output_file_button.grid(row = gui_row_iteration, column = 2)
        gui_row_iteration += 1
        self.sim_do_output_button = tk.Button(self, text="Save File", command = self.sim_output_save_file)   
        self.sim_do_output_button.grid(row = gui_row_iteration, column = 2)
        gui_row_iteration+= 1

        # math output file
        self.math_output_label_filepath = tk.Label(self, text="Math Output Filepath ")
        self.math_output_label_filepath.grid(row = gui_row_iteration, column = 0)
        self.math_output_file_entry = ttk.Entry(self, textvariable = self.math_output_filepath, text=self.math_output_filepath)
        self.math_output_file_entry.grid(row = gui_row_iteration, column = 1)
        self.math_output_file_button = tk.Button(self, text="...", command = self.math_output_filepath_dialog_button)
        self.math_output_file_button['command'] = self.math_output_filepath_dialog_button
        self.math_output_file_button.grid(row = gui_row_iteration, column = 2)
        gui_row_iteration += 1
        self.math_do_output_button = tk.Button(self, text="Save File", command = self.math_output_save_file)   
        self.math_do_output_button.grid(row = gui_row_iteration, column = 2)
        gui_row_iteration += 1

        # Plot Button to show math
        self.label_plot = tk.Label(self, text="4b. Plot Spins to Credits")
        self.label_plot.grid(row = gui_row_iteration, column = 0, columnspan = 3)
        gui_row_iteration += 1
        self.run_plot_button = tk.Button(self, text="4b. Plot Spins to Credits", command = self.plot_button_clicked)       
        self.run_plot_button.grid(row = gui_row_iteration, column = 1)
        gui_row_iteration += 1

        ### debug buttons ### (run the win once and set the outcome)
        ### reset credits button (separate from the 'build virtual slot'?)
        ### set jackpot
        ### set win

if __name__ == '__main__':
    """ main class: take input and call the GUI, which contains the simulator. """
    # GUI call here - this handles everything else, since it's ui / button driven 
    sim_gui = tkGui()
    sim_gui.mainloop()


    #### this is how it was originally called before the UI
    #settings; from file load or UI, later. 
    #reel_total = 3
    #paylines_total = 9
    # UI Values 
    #bet = 0.25
    # so, initially, each total bet is 2.25
    # .. simulator settings: 
    #initial_credits = 1000
    #simruns = 10
    # set the filepath - this is to be moved to the configuration file / ui input later.  literally the worst way to do this atm: 
    #filepath='/Users/jdyer/Documents/GitHub/JD-Programming-examples/Python/math_slot_simulator/PARishSheets.xlsx'
    # build slot machine with the filepath
#    sm = SlotMachine(filepath, reel_total, paylines_total, bet, initial_credits)
    # start the simulator using the slot machine. 
#    sim = Simulator(sm, simruns)