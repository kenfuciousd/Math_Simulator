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
import math
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

### slot machine class - meant to keep persistant data on its own state and 'spin reels' to give outcomes
class SlotMachine: 
    """Slot machine class, takes in the 'input' file, and a number of gui elements """ 
    # initialize, setting allowances to settings:
    def __init__(self, filepath, bet, initial_credits, debug_level, infinite_checked):
        self.input_filepath = filepath
        self.game_credits = initial_credits   # the 'wallet' value 
        self.initial_credits = initial_credits  #specifically to save the value for the infinite check
        self.bet = bet
        self.infinite_checked = infinite_checked
        #initialize data to be used in the local object namespace, so it's able to be referenced. 
        self.reels_sheetname = 'Reels_highvol'
        self.paytable_sheetname = 'Paytable_highvol'
        self.paylines_sheetname = 'Paylines'
        self.game_window = []
        self.paytable = []
        self.reels = []
        self.wildsymbols = []
        self.paylines = []
        self.paylines_total = 9 # 3x3 default value to be set later... in the paylines
        self.debug_level = debug_level
        # the math section.
        self.hit_total = 0
        self.maximum_liability = 0
        self.volitility = float(0)
        self.mean_pay = 0
        self.summation = 0
        self.this_win = 0    # value to be returned for tracking
        self.total_won = 0
        self.total_bet = 0
        # debug announcement; the place for initial conditions to get checked or set.
        if(self.debug_level >= 1):
            print(f"DEBUG LEVEL 1 - basic math and reel matching info")
        if(self.debug_level >= 2):
            print(f"DEBUG LEVEL 2 - most debugging information, descriptive")
            print(f"{self.input_filepath} .. was saved from {filepath}")
        if(self.debug_level >= 3):
            print(f"DEBUG LEVEL 3 - every other status message used for debugging - verbose")

        ### the reels, here, are the reel strips. 
        self.build_reels()
        # chooses the random positions for each of the reels, eventually add the total reel number to pass
        self.randomize_reels()
        #build paylines: read in file, store a paylines list to reference elsewhere - this is the map of how it checks for wins against the game window
        self.build_paylines()
        # paytable next, the reel lenghts are needed for math, along with the paylines  
        self.build_pay_table()
        #finally, build the 'game window'.. a 2 tier array/list where the symbols get set from the reels each spin, and what is checked against by the paylines
        self.build_game_window()
        #end initialization

    def build_paylines(self):
        #first payline: middle line; the 'reel positions'
        #paylines=[(0,1),(1,1),(2,1)]

        # this is what should be loaded from the excel sheet later
        #referenced by paylines[full-payline][payline-item-number][either 0 for reel, or 1 for position]
        #so paylines[0][2] is the third reel position to check at game_window[2][0], [2]reel three, [0]top position.
        #self.paylines
        self.payline_data = pd.read_excel(self.input_filepath, sheet_name=self.paylines_sheetname)

        self.paylines = []
        for idx, row in self.payline_data.iterrows():
            # for each row
            temprow = [] 
            for i in range(0, self.payline_data.shape[1]):
                temprow.append(row[i])
            if(self.debug_level >= 2):
                print(f"         **** the payline being added is: {temprow}")
            self.paylines.append(temprow)

        # to note: default here is for 3x3.  This determines our game window sizing. 
        #self.paylines=[
        #    [(0,0),(1,0),(2,0)],
        #    [(0,1),(1,1),(2,1)],
        #    [(0,2),(1,2),(2,2)],
        #    [(0,0),(1,1),(2,2)],
        #    [(0,2),(1,1),(2,0)],
        #    [(0,0),(1,1),(2,0)],
        #    [(0,1),(1,2),(2,1)],
        #    [(0,1),(1,0),(2,1)],
        #    [(0,2),(1,1),(2,2)]
        #]

    def build_reels(self):
        # v2 reel building, initialize for 5, build as many as needed. 
        self.reel1 = []
        self.reel2 = []
        self.reel3 = [] 
        self.reel4 = []
        self.reel5 = []

        ## this will be referenced by the reels anytime we need to check for columns
        self.reel_data = pd.read_excel(self.input_filepath, sheet_name=self.reels_sheetname)
        # we should do some testing about the reel data being good data.. but python will just complain either way

        if("Reel 5" in self.reel_data): # if the data contains 'reel'
            self.reel5 = self.reel_data['Reel 5']
            self.reels = 5
            self.reel5pos = 0
            print(f"{self.reel5}")
        if("Reel 4" in self.reel_data):
            self.reel4 = self.reel_data['Reel 4']
            self.reels = 4
            self.reel4pos = 0
            print(f"{self.reel4}")
        #else.. it's 3 reels. 
        else: 
            self.reels = 3
        self.reel3 = self.reel_data['Reel 3']
        self.reel3pos = 0
        self.reel2 = self.reel_data['Reel 2']
        self.reel2pos = 0
        self.reel1 = self.reel_data['Reel 1']
        self.reel1pos = 0    
        #except:
            #print(f" !! Not a good filename: {self.input_filepath} !!")
        # dataframe_var.shape to get dimensionality: (22,5)    .. so dataframe_var.shape[0] is the rows (depth) and [1] is the columns (width)

        # if there is a file at the spot, read it. ... this logic should probably be changed/added to the payline/paytable pieces..

    def randomize_reels(self):
        if(self.debug_level >= 2):
            print(f"        before randomize: {str(self.reel1pos)} {str(self.reel2pos)} {str(self.reel3pos)} " )
        self.reel1pos=random.randint(0,len(self.reel1)-1)
        self.reel2pos=random.randint(0,len(self.reel2)-1)
        self.reel3pos=random.randint(0,len(self.reel3)-1)
        if("Reel 5" in self.reel_data):            
            self.reel5pos=random.randint(0,len(self.reel5)-1)
            if(self.debug_level >= 1):
                print(f"        after randomization, reel positions: {str(self.reel1pos)}, {str(self.reel2pos)}, {str(self.reel3pos)}, {str(self.reel4pos)}, {str(self.reel5pos)} ")
        elif("Reel 4" in self.reel_data):
            self.reel4pos=random.randint(0,len(self.reel4)-1)
            if(self.debug_level >= 1):
                print(f"        after randomization, reel positions: {str(self.reel1pos)}, {str(self.reel2pos)}, {str(self.reel3pos)}, {str(self.reel4pos)} ")
        else:
            if(self.debug_level >= 1):
                print(f"        after randomization, reel positions: {str(self.reel1pos)}, {str(self.reel2pos)}, {str(self.reel3pos)} ")

    def adjust_credits(self,value):
        # bets should be negative values, wins or deposits positive
        if(value >= 0):
            self.total_won += value
        elif(value < 0):
            # negative to offset the negative value of the bet itself. 
            self.total_bet -= value
        if(self.debug_level >= 2):
            print("Adjusting credits at " + str(value))
        self.game_credits = np.round(float(self.game_credits) + value, 2)
        if(self.debug_level >= 1):
            print(f"    $$$$ Adjusted credits by {str(value)}, now game wallet at: {str(self.game_credits)}")

    def return_credits(self):
         return self.game_credits

    def reset_wildsymbols(self):
        """this function is used to reset the wildsymbols list, to assist the 'is_a_win' function, so that "any bars" or "any 7s", etc, don't get 'stuck' in the test """
        self.wildsymbols = ['W']
        #if(self.debug_level >= 3):
            #print("resetting wildsymbols: " + str(self.wildsymbols))

    # note will need to change these inputs, to allow for >3
    def build_game_window(self):
        #for now: 3 reels, more logic later - like sending a list of the positions, so it's size agnostic. 
        #     sets the window positions (reminder, game_window[row][reel])
        #if reel1 pos == 0 (or reel's 2 or three), then set (game_window[reel][0]) as reelN[len(reel1)-1)
        # else use reelN[reelposN-1]
        ##### 5 Reels have two configs: 5x3 and 5x5.  ... this is for 5x5..  but how do we tell the difference? is it in the paytables? becuase that basically defines that data...: 
        if("Reel 5" in self.reel_data):  
            # instantiating generic window
            self.game_window = [['gh1', 'gh6', 'gh11', 'gh16', 'gh21'], ['gh2', 'gh7', 'gh12', 'gh17', 'gh22'], ['gh3', 'gh8', 'gh13', 'gh18', 'gh23'], ['gh4', 'gh9', 'gh14', 'gh19', 'gh24'], ['gh5', 'gh10', 'gh15', 'gh20', 'gh25']]
            if(self.debug_level >= 1):
                print(str(reel1pos) + " " + str(reel2pos) + " " + str(reel3pos) + " " + str(len(self.reel1)-1) + " " + str(self.reel1[len(self.reel1)-1]))
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
            if(self.reel4pos==0):
                self.game_window[3][0]=self.reel4[len(self.reel4)-1]
            else:
                self.game_window[3][0]=self.reel4[self.reel4pos-1]  
            if(self.reel5pos==0):
                self.game_window[4][0]=self.reel5[len(self.reel5)-1]
            else:
                self.game_window[4][0]=self.reel5[self.reel5pos-1]  
            #the middle row is always true
            self.game_window[0][1] = self.reel1[self.reel1pos]
            self.game_window[1][1] = self.reel2[self.reel2pos]
            self.game_window[2][1] = self.reel3[self.reel3pos]
            self.game_window[3][1] = self.reel4[self.reel4pos]
            self.game_window[4][1] = self.reel5[self.reel5pos]
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
            if(self.reel3pos==len(self.reel3)-1):
                self.game_window[3][2]=self.reel3[0]
            else:
                self.game_window[3][2]=self.reel4[self.reel4pos+1]
            if(self.reel4pos==len(self.reel4)-1):
                self.game_window[4][2]=self.reel4[0]
            else:
                self.game_window[4][2]=self.reel4[self.reel3pos+1]

            ##handling for reels 4 and 5 could be here, when configured. If reels==5, do the same thing as above for all three positions, but for 5x5
            print(f"    ****    Found 5 reels, not yet implemented")

        elif("Reel 4" in self.reel_data):
            self.game_window = [['gh1', 'gh5', 'gh9', 'gh13'], ['gh2', 'gh6', 'gh10', 'gh14'], ['gh3', 'gh8', 'gh11', 'gh15'], ['gh4', 'gh8', 'gh12', 'gh16']]
            if(self.debug_level >= 2):
                print(f"    >> {str(reel1pos)} {str(reel2pos)} {str(reel3pos)} {str(reel4pos)} + {str(len(self.reel1)-1)} {str(self.reel1[len(self.reel1)-1])}")
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
            if(self.reel4pos==0):
                self.game_window[3][0]=self.reel4[len(self.reel4)-1]
            else:
                self.game_window[3][0]=self.reel4[self.reel4pos-1]             
            #the middle row is always true
            self.game_window[0][1] = self.reel1[self.reel1pos]
            self.game_window[1][1] = self.reel2[self.reel2pos]
            self.game_window[2][1] = self.reel3[self.reel3pos]
            self.game_window[3][1] = self.reel4[self.reel4pos]
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
            print(f"    |||| reel 4 {self.reel4pos}, and {self.reel4[self.reel4pos+1]}")
            if(self.reel4pos==len(self.reel4)-1):
                self.game_window[3][3]=self.reel4[0]
            else:
                self.game_window[3][3]=self.reel4[self.reel4pos+1]
            ##handling for reels 4 and 5 could be here, when configured. If reels==5, do the same thing as above for all three positions, but for 5x5
            print(f"    ****    Found 4 reels, ")

        elif("Reel 3" in self.reel_data):
            self.game_window = [['gh1', 'gh4', 'gh7'], ['gh2', 'gh5', 'gh8'], ['gh3', 'gh6', 'gh9']]
            #if(self.debug_level >= 1):
                #print(f"    {str(self.reel1pos)} + {str(self.reel2pos)} + {str(self.reel3pos)} + {str(len(self.reel1)-1)} + {str(self.reel1[len(self.reel1)-1])} ")
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
        else:
            #output logging goes here. 
            print("Check settings. Choose Reel +1 and Reel 2 and Reel 3, + Reel 4, + Reel 5 as labels for the reel columns.")
            quit()
        if(self.debug_level >= 3):
            print(self.game_window)

    def build_pay_table(self):
        #to replace with loading it in...  so in excel, 4 columns, reelNum text fields followed by the win amount
        #accessible in object with:  paytable[each_win_line from 0 to len-1][0 to len-1 for each symbol and the value]
        ##
        #### last value should be credits, to multiply vs the bet.. not dollar values
        self.paytable_data = pd.read_excel(self.input_filepath, sheet_name=self.paytable_sheetname)
        self.paytable = []
        self.mean_pay = 0
        for idx, row in self.paytable_data.iterrows():
            # for each row
            temprow = [] 
            for i in range(0, self.paytable_data.shape[1]):
                temprow.append(row[i])
            self.paytable.append(temprow)

        if(self.debug_level >= 2):
            print(f"        Paytable: {self.paytable}")

        # Paytable Math begins here. 
        total_combinations = 0
        # step 1. mean pay
        for line in self.paytable:
            #print(f"line {line[len(line)-1]}")
            self.mean_pay += line[len(line)-1]
        self.mean_pay = self.mean_pay / len(self.paytable)
        if(self.debug_level >= 2):
            print(f"    Paytable Mean Pay is {self.mean_pay}")
        #this may be unnecessary... the paytable math  
        #self.total_combinations = len(self.reel1) * len(self.reel2) * len(self.reel3)
        #if(self.reels >= 4):
        #    self.total_combinations *= len(self.reel4)
        #if(self.reels == 5):
        #    self.total_combinations *= len(self.reel5)
        #if(self.debug_level >= 2):
        #    print(f"        Total Combinations: {total_combinations}")        

        #self.paytable = [
        #    ('W','W','W',12.5),
        #    ('B7','B7','B7',11.25),
        #    ('R7','R7','R7',10.75),
        #    ('*7','*7','*7',10),
        #    ('3B','3B','3B',6.50),
        #    ('2B','2B','2B',6),
        #    ('1B','1B','1B',5.5),
        #    ('*B','*B','*B',3)
        #]
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

    # call win determination (send each specified payline's values to check against the paytable, #operations are paylines times paytable rows)
    def is_a_win(self):
        #check payline from the reels, sending over the gamewindow array
        # this should cycle the payline list, (each line pulling the 3 to 5 coordinates) 
        # then testing each of those against each paytable line
        # ... with special consideration for wilds, denoted *
        # so..  for each payline, grab the symbols from the game window compare to the whole paytable win list 
        #if it matches one of those lines (wild logic here), then pull the len-1 entry for that line
        iteration = 0
        total_win = 0
        self.this_win = 0
        for line in self.paylines:
            symbols=[]
            winbreak = 0
            iteration += 1
            if(self.debug_level >= 2):
                print(f"    **** debug: in win line checking, line {line}")
            for reel_pos in line:
                if(self.debug_level >= 2):
                    print(f"        **** debug: reel pos: {int(reel_pos[0])}")
                symbols.append(self.game_window[int(reel_pos[0])][int(reel_pos[2])])
            if(self.debug_level >= 1):
                print(f"    testing payline {iteration} with symbols: {str(symbols)}")  # this is pulling game window correctly
            #test against paytable
            self.reset_wildsymbols()
            for winline in self.paytable:
                for reelnum in range(0, self.reels):
                    # reworking logic..
                    if(self.debug_level >= 3):
                        print("             - testing reel: " + str(reelnum+1) + " for " + str(symbols[reelnum]) + " versus " + str(winline[reelnum]))
                    if "*" in str(winline[reelnum]):
                        #print("Found an Any Type Symbol")
                        if winline[reelnum] == '*B':
                            for sym in ['1B','2B', '3B']:
                            # eventually, logic to include the right ones from the reel.
                                self.wildsymbols.append(sym)
                            #if(self.debug_level >= 3):
                                #print("            - appended Bars to wild symbols")
                        elif winline[reelnum] == '*7':
                            for sym in ['B7','R7']:
                                self.wildsymbols.append(sym)
                            #if(self.debug_level >= 3):
                                #print("            - appended 7s to wild symbols")
                        else: 
                            # any symbol.. for 4 and 5 reels to ignore specific spots (allowing different length win lines)
                            self.wildsymbols.append('*')
                       # other wild symbols would go here. 

                    # win logic                     ### NOTE: Winning logic is *HERE* 
                    if((symbols[reelnum] == winline[reelnum]) or (symbols[reelnum] in self.wildsymbols)):
                        #if they do not match at any time, return false 
                        if(self.debug_level >= 1):
                            print("        Match symbol " + symbols[reelnum]  + " against the paytable symbol " + winline[reelnum] + " on reelnum: " + str(reelnum+1)) # + " and testing reels: " + str(self.reels))
                        #payout is the last entry on the winline
                        if(reelnum + 1 == self.reels):
                            self.reset_wildsymbols()
                            # this is where the hit_total is added, should go off for each winline found 
                            self.hit_total += 1
                            if(self.debug_level >= 2):
                                print(f"    +=+=+=+= summation is currently {self.summation} and about to add {(self.mean_pay - (winline[len(winline)-1] ) ) ** 2}")
                            self.summation += (self.mean_pay - (winline[len(winline)-1] ) ) ** 2     ##* self.bet) ) ** 2

                            total_win += winline[len(winline)-1] * self.bet 
                            if(self.debug_level >= 1):
                                print(f"    !!!! WIN! awarding {str(winline[len(winline)-1])} credits, meaning total win is ${total_win} and the winline: {str(symbols)} !!!!")
                            self.adjust_credits( winline[len(winline)-1] * self.bet)  ### this should use credits, so bet value x the payline amount

                            if(self.debug_level >= 2):
                                print(f"    +=+=+=+= summation is now {self.summation}, which added: ({self.mean_pay} minus {(winline[len(winline)-1])}) squared. Now at {self.hit_total} win 'hits' ")
                            winbreak = 1
                            #return True
                            self.reset_wildsymbols()                            
                    else:
                        self.reset_wildsymbols()

                        break
                        #else, if it's the last reel, and it didn't match, 
                ##### double check above
                # this is to not give double rewards to the same line - in python, the test is nested, and break doesn't work inside of it due to logic. 
                if(winbreak == 1):
                    winbreak = 0
                    break
        # end of the payline checking, any totaling happens here. 
        if(self.debug_level >= 1):
            print(f"    +=+=+=+=  current summation: {self.summation} ")
        if(self.debug_level >= 2):
            print(f"        maximum_liability is {self.maximum_liability} and this total win was {total_win}")
        if(total_win > self.maximum_liability):
            if(self.debug_level >= 1):
                print(f"    New Maximum liability: {total_win}")
            self.maximum_liability = total_win
        self.this_win = total_win  #This will be grabbed every 'spin'


    # spin reels: a major part of the functionality 
    def spin_reels(self):
        if(self.debug_level >= 3):
            print("            bet is " + str(self.bet) + " and paylines is " + str(self.paylines_total))
        total_bet = self.bet * float(self.paylines_total)
        if(self.debug_level >= 3):
            print(f"            checking credits: {self.game_credits}  <  {str(total_bet)}")
        if(self.debug_level >= 3):
            print("            betting: " + str(total_bet*-1))
        self.adjust_credits(total_bet * -1)
        #STUB: remove wallet value: bet x paylines; check to see if player has enough
        #randomly choose reel positions for each of the reels
        self.randomize_reels()
        self.build_game_window()
        self.is_a_win()


class Simulator():
    """ simulator class: takes in the SlotMachine class object, does stuff and tracks it. """
    def __init__(self, sm, simnum, debug_level):
        self.simnum = simnum
        self.sm = sm
        self.this_bet = sm.bet * float(sm.paylines_total)
        self.incremental_credits = []
        self.spins = []
        self.df_dict = ["credits"] # takes up the header line and lets us start at iteration 1 for data purposes
        self.debug_level = debug_level
        self.run_sim()
        #self.plot_result()   # the automatic plotting was causing issues with things hanging until it closed. 

    def run_sim(self):
        for iteration in range(self.simnum):
            #print("spinning")
            if( self.this_bet > float(self.sm.game_credits) ):
                # can't really send back a status to the gui?? 
                #simgui.slot_check.set("[Reset Slot]")
                if(self.debug_level >= 2):
                    print(f"    $$$$ no futher credits, if this is true: {self.sm.infinite_checked} then we should see credits added and spins continue")
                if(self.sm.infinite_checked == True):
                    self.sm.game_credits += float(self.sm.initial_credits)
                    if(self.debug_level >= 1):
                        print(f"    $$$$ adding {self.sm.initial_credits}, credits should now reflect that at: {self.sm.game_credits} ")
                else:    
                    print("!!!! Not enough credits, $" + str(self.this_bet) + " is required.")
                    break
            else: #main spinning game loop 
                # some of the busy parts of the simulator. spin the slotmachine(sm)'s reels and track the data
                # choosing a dictionary for the df_dict var because it's easy to convert to a DataFrame later. 
                if(self.debug_level >= 1):
                    print(f"spin {str(iteration+1)} and credits ${str(self.sm.return_credits())}")
                self.sm.spin_reels()
                self.incremental_credits.append(self.sm.return_credits())
                self.spins.append(iteration+1)
                self.df_dict.insert(iteration+1, self.sm.this_win)
                if(self.debug_level >= 3):
                    print(f"    spin {str(iteration)} and credits ${str(self.sm.return_credits())} and added to the dictionary: {self.df_dict[iteration]}")

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
        self.debug_level_default = 1
        #initial gui settings and layout
        self.geometry("500x670")
        self.title("Slot Simulator")
        self.columnconfigure(0, weight = 1)
        self.columnconfigure(1, weight = 1)
        self.columnconfigure(2, weight = 1)

        # default text/value entries
        self.bet = StringVar(self, value = "0.25")  ## so I need to set this as a string in order to get a decimal.
        self.slot_ready = False
        self.infinite_checked = BooleanVar(self, value=False)
        # .. simulator settings: 
        self.initial_credits = IntVar(self, value = 100)
        self.simruns = IntVar(self, value = 500)
        self.input_filepath = StringVar(self, value = "./PARishSheets.xlsx") 
        self.sim_output_filepath = StringVar(self, value = "./simdata.csv")
        self.math_output_filepath = StringVar(self, value = "./mathdata.csv")
        self.payline_number = IntVar(self, value = 0)
        self.payline_totalbet = DoubleVar(self, value = 0 )
        self.status_box = StringVar(self, value = "[Select Input File at 1., or/then Click 2.]")
        # simulator spins/credits data
        self.df = pd.DataFrame()
        # debug level, a gui element to decide if we want extra output. 
        self.debug_level = IntVar(self, value = self.debug_level_default)
        # dictionary with math, next? 
        self.hit_freq = IntVar(self, value = 0)
        self.max_liability = IntVar(self, value = 0)        
        self.volatility = DoubleVar(self, value = 0)
        self.return_to_player = DoubleVar(self, value = 0)
        # finally for init, create the gui itself, calling the function
        self.create_gui()

    #output buttons - decided to make them separate in case we want to do different things with them
    ##### currently broken.. when using .get() .. meaning it's breaking out of the text box string format...
    def input_filepath_dialog_button(self): 
        #clear out the old entries, then reset. 
        if(self.debug_level >= 1):
            print(f"    input was {self.input_filepath.get()}")  
        self.input_filepath.set("")
        self.input_file_entry.select_clear()     
        # clearing out the variables, don't work 
        the_input = fd.askopenfilename(initialdir=os.curdir, title="Select A File", filetypes=(("excel files","*.xlsx"), ("all files","*.*")) )
        self.input_filepath.set(the_input)
        if(self.debug_level >= 2):
            print(f"        input is {self.input_filepath.get()}")
        self.input_file_entry.textvariable=self.input_filepath.get()
        if(self.debug_level >= 3):
            print(f"            and the entry is {self.input_file_entry.get()}")

    def sim_output_filepath_dialog_button(self): 
        self.sim_output_filepath.set(fd.askopenfilename(initialdir=os.curdir, title="Select A File", filetypes=(("csv files","*.csv"), ("all files","*.*")) ) )
        if(self.debug_level >= 1):
            print(f"    ouput filepath is {self.sim_output_filepath}")       
        self.sim_output_file_entry.textvariable=self.sim_output_filepath.get()

    def math_output_filepath_dialog_button(self): 
        self.math_output_filepath.set(fd.askopenfilename(initialdir=os.curdir, title="Select A File", filetypes=(("csv files","*.csv"), ("all files","*.*")) ) )
        if(self.debug_level >= 1):
            print(f"    math output file is {self.math_output_filepath}")
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
        if(self.debug_level.get() >= 1):
            print(f"    Sim Output Saving... {str(self.sim_output_filepath.get())}")

    def math_output_save_file(self):
        data = self.df #### this will be a different data set.....
        #print(data)
        # if file does not exist, create first.. then append
        #print(str(self.math_output_filepath.get()))
        if(os.path.exists(str(self.math_output_filepath)) == False):
            with open(str(self.math_output_filepath.get()), 'w') as fp:
                fp.close()
        data.to_csv(str(self.math_output_filepath.get()))
        if(self.debug_level.get() >= 1):
            print(f"    Math Output File Saving... {str(self.math_output_filepath.get())}")

    #### This is where the magic happens in the GUI, part 1 ####
    def build_slot_button(self):
        # use the current values
        input_filepath = self.input_filepath.get() #this didnt like .get()
        #print(f" after build slot, input filepath clicked is: {input_filepath}")
        bet = float(self.bet_entry.get())
        initial_credits = self.credit_entry.get()
        if(self.debug_level.get() >= 3):
            print(f"            Slot Machine geting passed: {input_filepath}, {bet}, {initial_credits}, {self.debug_level.get()} and inf checked? {self.infinite_checked.get()}")
        self.sm = SlotMachine(input_filepath, bet, initial_credits, self.debug_level.get(), self.infinite_checked.get())
        self.slot_ready = True
        self.status_box.set("[2. Slot Built - Credits Loaded]")
        self.payline_number.set(len(self.sm.paylines))
        self.payline_totalbet.set("{:.2f}".format(int(self.payline_number.get()) * float(self.bet_entry.get())))
        # a gui checkbox to show it was done? in the build column in slot 0?

    #### This is where the magic happens in the GUI, part 2 ####
    def sim_button_clicked(self):
        #start simulation here...
        #print("buttonpress")
        if(self.slot_ready == True):
            self.status_box.set("[3. Done - Click 2 to Rebuild Slot]")            
            self.sim = Simulator(self.sm, self.simruns.get(), self.debug_level.get())   # simulator call 
            self.df = pd.DataFrame(self.sim.df_dict)                                    # pull the saved simulator dat
           
            #print(f" So here is what is returned from the SIM: \n {str(self.df)}")
            ######math goes here for output
            if(self.debug_level.get() >= 2):
                print(f"        hit info for math, total hits {self.sm.hit_total} and simulator runs: {self.simruns.get()}")
            hfe = ( self.sm.hit_total / self.simruns.get() )  * 100   #### is this needed? it's used in the templates file... 
            self.hit_freq.set(str(round(hfe, 2))+"%")
            ml = self.sm.maximum_liability
            self.max_liability.set("$"+str(ml))
            #### volatility goes here. ### 
            if(self.debug_level.get() >= 1):
                print(f"    ^^^^ the volatility math: {self.sm.summation} / {self.simruns.get() * (len(self.sm.paytable) + 1)} = {self.sm.summation/(self.simruns.get() * (len(self.sm.paytable) + 1))}.. sqrt is {math.sqrt( self.sm.summation / (self.simruns.get() * (len(self.sm.paytable) + 1) ))}, and so with * 1.96 the volatility index is {math.sqrt( self.sm.summation / (self.simruns.get() * (len(self.sm.paytable) + 1) )) * 1.96} ")
            volatilitymath = math.sqrt( self.sm.summation / (self.simruns.get() * (len(self.sm.paytable) + 1) ) ) * 1.96
            self.volatility.set(round(volatilitymath, 2))
            # RTP
            if(self.debug_level.get() >= 1):
                print(f"    $$$$ RTP is {self.sm.total_won} / {self.sm.total_bet} = {(self.sm.total_won / self.sm.total_bet)} ")
            self.return_to_player.set("{:.2f}".format(self.sm.total_won / self.sm.total_bet * 100)+"%")
            # finally, record / print our final values as a status
            if(self.debug_level.get() >= 0):
                print(f"Final values, at spin {self.sim.spins[len(self.sim.spins)-1]}, the final credit value was {self.sim.incremental_credits[len(self.sim.incremental_credits)-1]}" )
            print("Simulation Complete")
        else:
            self.status_box.set("[->2. Click 2 to Build or reload]")
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
        
        #simulator settings entries
        self.label_debug = tk.Label(self, text="Debug Level: 0 (Silent) through 3 (Verbose) ")
        self.label_debug.grid(row = gui_row_iteration, column = 0, columnspan=2, sticky=E)
        self.debug_entry = ttk.Entry(self, width = 8, textvariable = self.debug_level)
        self.debug_entry.grid(row = gui_row_iteration, column = 2)
        gui_row_iteration += 1
        self.label_bet = tk.Label(self, text="Bet per Line")
        self.label_bet.grid(row = gui_row_iteration, column = 0, columnspan=2, sticky=E)
        self.bet_entry = ttk.Entry(self, width = 8, textvariable = self.bet)
        self.bet_entry.grid(row = gui_row_iteration, column = 2)
        gui_row_iteration += 1
        self.label_cred = tk.Label(self, text="Starting Dollars ")
        self.label_cred.grid(row = gui_row_iteration, column = 0, columnspan=2, sticky=E)
        self.credit_entry = ttk.Entry(self, width = 8, textvariable = self.initial_credits)
        self.credit_entry.grid(row = gui_row_iteration, column = 2)
        gui_row_iteration += 1
        self.label_infinite = tk.Label(self, text="Infinite Credits: ")
        self.label_infinite.grid(row = gui_row_iteration, column = 0, columnspan=2, sticky=E)
        self.infinite_check = ttk.Checkbutton(self, variable = self.infinite_checked, onvalue = True, offvalue = False)
        self.infinite_check.grid(row = gui_row_iteration, column = 2)        
        gui_row_iteration += 1

        # build slot button
        self.label_build_slot = tk.Label(self, text="2. Build Virtual Slot ")
        self.label_build_slot.grid(row = gui_row_iteration, column = 0, columnspan = 3, sticky=W, padx=15)
        gui_row_iteration += 1
        self.run_slots_button = tk.Button(self, text="2. Build Virtual Slot", command = self.build_slot_button)
        self.run_slots_button.grid(row = gui_row_iteration, column = 0, sticky=W, padx=15)
        gui_row_iteration += 1

        # the status box. intentionally making it a bit obnoxious to catch the eye and because I want to change how this works later. 
        self.status_box_box = tk.Label(self, textvariable=self.status_box, bg = "dodgerblue1", fg = "ghostwhite")
        self.status_box_box.grid(row = gui_row_iteration, columnspan=3, pady=15 )
        gui_row_iteration += 1

        # payline explanation
        self.label_payinfo = tk.Label(self, text="Paylines")
        self.label_payinfo.grid(row = gui_row_iteration, column = 0, columnspan=2, sticky=E)
        self.paylines_entry = ttk.Entry(self, width = 8, state='readonly', textvariable = self.payline_number)
        self.paylines_entry.grid(row = gui_row_iteration, column = 2)
        gui_row_iteration += 1
        self.label_payinfo = tk.Label(self, text="Total Bet (bet per line * paylines): ")
        self.label_payinfo.grid(row = gui_row_iteration, column = 0, columnspan=2, sticky=E)
        self.paylines_entry = ttk.Entry(self, width = 8, state='readonly', textvariable = self.payline_totalbet)
        self.paylines_entry.grid(row = gui_row_iteration, column = 2)
        gui_row_iteration += 1

        # simulator info
        self.label_simruns = tk.Label(self, text="Simulator Total Spins" )
        self.label_simruns .grid(row = gui_row_iteration, column = 0, columnspan=2, sticky=E)
        self.simrun_entry = ttk.Entry(self, width = 10, textvariable = self.simruns)
        self.simrun_entry.grid(row = gui_row_iteration, column = 2, pady=5)
        gui_row_iteration += 1

        # Run Button
        self.label_sim = tk.Label(self, text="3. Run Simulation")
        self.label_sim.grid(row = gui_row_iteration, column = 0, columnspan = 3, sticky=W, padx=15)
        gui_row_iteration += 1
        self.run_sim_button = tk.Button(self, text="3. Run Simulation", command = self.sim_button_clicked)       
        self.run_sim_button.grid(row = gui_row_iteration, column = 0, sticky=W, padx=15)
        gui_row_iteration += 1

        #sim label
        self.label_output = tk.Label(self, text="4a. Save Outputs")
        self.label_output.grid(row = gui_row_iteration, column = 0, columnspan = 3, pady=5)
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
        #self.math_output_label_filepath = tk.Label(self, text="Math Output Filepath ")
        #self.math_output_label_filepath.grid(row = gui_row_iteration, column = 0)
        #self.math_output_file_entry = ttk.Entry(self, textvariable = self.math_output_filepath, text=self.math_output_filepath)
        #self.math_output_file_entry.grid(row = gui_row_iteration, column = 1)
        #self.math_output_file_button = tk.Button(self, text="...", command = self.math_output_filepath_dialog_button)
        #self.math_output_file_button['command'] = self.math_output_filepath_dialog_button
        #self.math_output_file_button.grid(row = gui_row_iteration, column = 2)
        #gui_row_iteration += 1
        #self.math_do_output_button = tk.Button(self, text="Save File", command = self.math_output_save_file)   
        #self.math_do_output_button.grid(row = gui_row_iteration, column = 2)
        #gui_row_iteration += 1

        # Plot Button to show math
        self.label_plot = tk.Label(self, text="4b. Plot Spins to Credits")
        self.label_plot.grid(row = gui_row_iteration, column = 0, columnspan = 3, sticky=W, padx=15)
        gui_row_iteration += 1
        self.run_plot_button = tk.Button(self, text="4b. Plot Spins to Credits", command = self.plot_button_clicked)       
        self.run_plot_button.grid(row = gui_row_iteration, column = 0, sticky=W, padx=15)
        gui_row_iteration += 1

        ### reset credits button (separate from the 'build virtual slot'?)
        ### math output area
        # Hit frequency (hits / spins)
        self.label_hit_freq = tk.Label(self, text="Hit Frequency  ")
        self.label_hit_freq.grid(row = gui_row_iteration, column = 0, columnspan=2, sticky=E, pady=5)
        self.hit_freq_entry = ttk.Entry(self, width = 8, textvariable = self.hit_freq, state='readonly')
        self.hit_freq_entry.grid(row = gui_row_iteration, column = 2)
        gui_row_iteration += 1
        # Max Liability (biggest win)
        self.label_max_liability = tk.Label(self, text="Max Liability  ")
        self.label_max_liability.grid(row = gui_row_iteration, column = 0, columnspan=2, sticky=E)
        self.max_liability_entry = ttk.Entry(self, width = 8, textvariable = self.max_liability, state='readonly')
        self.max_liability_entry.grid(row = gui_row_iteration, column = 2)
        gui_row_iteration += 1
        # Volatility  (see documentation, it's complex...  volatility  = square root of: (  ( ( sum(win values - mean pay) ) ^^ 2 ) / total spins  )
        self.label_volatility = tk.Label(self, text="Volatility Index ")
        self.label_volatility.grid(row = gui_row_iteration, column = 0, columnspan=2, sticky=E)
        self.volatility_entry = ttk.Entry(self, width = 8, textvariable = self.volatility, state='readonly')
        self.volatility_entry.grid(row = gui_row_iteration, column = 2)
        gui_row_iteration += 1
        # Return to Player
        self.label_rtp = tk.Label(self, text="Return to Player Percentage (RTP) ")
        self.label_rtp.grid(row = gui_row_iteration, column = 0, columnspan=2, sticky=E)
        self.rtp_entry = ttk.Entry(self, width = 8, textvariable = self.return_to_player, state='readonly')
        self.rtp_entry.grid(row = gui_row_iteration, column = 2)
        gui_row_iteration += 1
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