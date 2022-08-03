import sys
import os
import os.path
import math
import random
import numpy as np        # rounding
import pandas as pd

class SlotMachine(): 
    """Slot machine class, takes in a number of gui elements: filepath, bet, initial credits, debug level, and infinite cash check box boolean """ 
    # initialize, setting allowances to settings:
    def __init__(self, filepath, bet, initial_credits, debug_level, infinite_checked):
        # initialization values 
        self.input_filepath = filepath
        self.game_credits = initial_credits   # the 'wallet' value 
        self.initial_credits = initial_credits  #specifically to save the value for the infinite check
        self.bet = bet
        self.infinite_checked = infinite_checked
        # original 3 reel test data
        self.reels_sheetname = 'Reels'
        self.paytable_sheetname = 'Paytable'
        self.paylines_sheetname = 'Paylines'
        # this section is to define where we get our theoretical/pre-calculated values from.. 
        self.rtp_sheetname = 'RTP'   # it doesn't like 'Ways/Pays' in excel
        self.vi_sheetname = 'RTP'
        self.rtp_column = 'RTP'
        self.vi_column = 'Volatility'
        ## examples, uncomment to override the original sheet values
        # 3 reel low volatility
        #self.reels_sheetname = 'Reels_lowvol'
        #self.paytable_sheetname = 'Paytable_lowvol'
        #self.paylines_sheetname = 'Paylines'
        # 3 reel high volatility 
        #self.reels_sheetname = 'Reels_highvol'
        #self.paytable_sheetname = 'Paytable_highvol'
        #self.paylines_sheetname = 'Paylines'      
        # 5 reels, Marissa's original setup 
        self.reels_sheetname = 'Reels5'
        self.paytable_sheetname = 'Paytable5'
        self.paylines_sheetname = 'Paylines25'        
        self.rtp_sheetname = 'RTP5'   # it doesn't like 'Ways/Pays' in excel
        self.vi_sheetname = 'RTP5'
        # ad hoc, a 5 reel with *M and *F 3/4/5x paytable lines added;
        #self.reels_sheetname = 'Reels5'
        #self.paytable_sheetname = 'Paytable5_withwilds'
        #self.paylines_sheetname = 'Paylines25'
        
        self.game_window = []
        self.paytable = []
        self.reels = []
        self.wildsymbols = []
        self.paylines = []
        self.paylines_total = 9 # 3x3 default value to be set later... in the paylines
        self.debug_level = debug_level
        # the math section.
        self.wintoggle = 0
        self.hit_total = 0
        self.maximum_liability = 0
        self.volitility = float(0)
        self.mean_pay = 0
        self.summation = 0
        self.this_win = 0    # value to be returned for tracking
        self.total_won = 0
        self.total_bet = 0
        self.rtp = 0
        self.vi = 0
        # debug announcement; the place for initial conditions to get checked or set.
        if(self.debug_level >= 1):
            print(f"DEBUG LEVEL 1 - basic math and reel matching info")
        if(self.debug_level >= 2):
            print(f"DEBUG LEVEL 2 - most debugging information, descriptive")
            print(f"the local variable {self.input_filepath} .. was saved from input {filepath}")
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
        #print (f"!-!-        paylines total is {len(self.paylines)}")
        self.paylines_total = len(self.paylines) # very important, as this defaults to 9 for 3x3 

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
        # We always want these
        self.reel3 = self.reel_data['Reel 3']
        self.reel3 = self.reel3.dropna()
        self.reel3pos = 0
        self.reel2 = self.reel_data['Reel 2']
        self.reel2 = self.reel2.dropna()
        self.reel2pos = 0
        self.reel1 = self.reel_data['Reel 1']
        self.reel1 = self.reel1.dropna()
        self.reel1pos = 0    
        if("Reel 4" in self.reel_data):
            self.reel4 = self.reel_data['Reel 4']
            self.reel4 = self.reel4.dropna()
            self.reels = 4
            self.reel4pos = 0
            #print(f"{self.reel4}")
     #       if(self.debug_level >= 1):
     #           print(f"     |||| reel lengths: {str(len(self.reel1))}, {str(len(self.reel2))}, {str(len(self.reel3))}, {str(len(self.reel4))}")
        if("Reel 5" in self.reel_data): # if the data contains 'reel'
            self.reel5 = self.reel_data['Reel 5']
            self.reel5 = self.reel5.dropna()
            self.reels = 5
            self.reel5pos = 0
            #print(f"{self.reel5}")
            if(self.debug_level >= 1):
                print(f"     |||| reel lengths: {str(len(self.reel1))}, {str(len(self.reel2))}, {str(len(self.reel3))}, {str(len(self.reel4))}, {str(len(self.reel5))}")
        #else.. it's 3 reels. 
        else: 
            self.reels = 3
            if(self.debug_level >= 1):
                print(f"     |||| reel lengths: {str(len(self.reel1))}, {str(len(self.reel2))}, {str(len(self.reel3))}")

        #except:
            #print(f" !! Not a good filename: {self.input_filepath} !!")
        # dataframe_var.shape to get dimensionality: (22,5)    .. so dataframe_var.shape[0] is the rows (depth) and [1] is the columns (width)

        # if there is a file at the spot, read it. ... this logic should probably be changed/added to the payline/paytable pieces..

    def randomize_reels(self):
        #if(self.debug_level >= 2):
        #    print(f"        before randomize: {str(self.reel1pos)} {str(self.reel2pos)} {str(self.reel3pos)} " )
        self.reel1pos=random.randint(0,len(self.reel1)-1)
        self.reel2pos=random.randint(0,len(self.reel2)-1)
        self.reel3pos=random.randint(0,len(self.reel3)-1)
        if("Reel 5" in self.reel_data):            
            self.reel5pos=random.randint(0,len(self.reel5)-1)
            self.reel4pos=random.randint(0,len(self.reel4)-1)            
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
        if(self.debug_level >= 3):
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
        """ this is where the game window logic is handled, using the SlotMachine's variables - mechanical version"""
        # if reel1 pos == 0 (or reel's 2 or three), then set (game_window[reel][0]) as reelN[len(reel1)-1)
        # else use reelN[reelposN-1]
        ##### 5 Reels have two configs: 5x3 and 5x5.  ... this is for 5x5..  but how do we tell the difference? is it in the paytables? becuase that basically defines that data...: 
        if("Reel 5" in self.reel_data):  
            # initializing the generic window
            self.game_window = [['gh1', 'gh6', 'gh11', 'gh16', 'gh21'], ['gh2', 'gh7', 'gh12', 'gh17', 'gh22'], ['gh3', 'gh8', 'gh13', 'gh18', 'gh23'], ['gh4', 'gh9', 'gh14', 'gh19', 'gh24'], ['gh5', 'gh10', 'gh15', 'gh20', 'gh25']]
            if(self.debug_level >= 2):
                print(f"    **** debug: reel positions at: {str(self.reel1pos)} + {str(self.reel2pos)} + {str(self.reel3pos)} + {str(self.reel4pos)} + {str(self.reel5pos)} " )
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
            if(self.reel4pos==len(self.reel4)-1):
                self.game_window[3][2]=self.reel4[0]
            else:
                self.game_window[3][2]=self.reel4[self.reel4pos+1]
            if(self.reel5pos==len(self.reel5)-1):
                self.game_window[4][2]=self.reel5[0]
            else:
                self.game_window[4][2]=self.reel5[self.reel5pos+1]
            ##handling for reels 4 and 5 could be here, when configured. If reels==5, do the same thing as above for all three positions, but for 5x5
            if(self.debug_level >= 2):
                print(f"    ****    Found 5 reels, only 5x3 available at this time")
        # 4x3 - white hot 7s, but per Scott going to not use at present. this wasn't fully working
        elif("Reel 4" in self.reel_data):
            self.game_window = [['gh1', 'gh5', 'gh9', 'gh13'], ['gh2', 'gh6', 'gh10', 'gh14'], ['gh3', 'gh8', 'gh11', 'gh15'], ['gh4', 'gh8', 'gh12', 'gh16']]
            if(self.debug_level >= 2):
                print(f"    **** debug: reel positions at: {str(reel1pos)} {str(reel2pos)} {str(reel3pos)} {str(reel4pos)} + {str(len(self.reel1)-1)} {str(self.reel1[len(self.reel1)-1])}")
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
            #print(f"    |||| reel 4 {self.reel4pos}, and {self.reel4[self.reel4pos+1]}")
            if(self.reel4pos==len(self.reel4)-1):
                self.game_window[3][3]=self.reel4[0]
            else:
                self.game_window[3][3]=self.reel4[self.reel4pos+1]
            ##handling for reels 4 and 5 could be here, when configured. If reels==5, do the same thing as above for all three positions, but for 5x5
            #print(f"    ****    Found 4 reels, ")

        elif("Reel 3" in self.reel_data):
            self.game_window = [['gh1', 'gh4', 'gh7'], ['gh2', 'gh5', 'gh8'], ['gh3', 'gh6', 'gh9']]
            if(self.debug_level >= 2):
                print(f"        **** debug: reel positions at: {str(self.reel1pos)} + {str(self.reel2pos)} + {str(self.reel3pos)} ")
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
        # scrub np.nan to test for 5x/4x/3x paytable lines 
        self.mod_paytable_data = self.paytable_data.fillna("NaN")

        self.paytable = []
        self.mean_pay = 0
        for idx, row in self.mod_paytable_data.iterrows():
            # for each row
            temprow = [] 
            for i in range(0, self.mod_paytable_data.shape[1]):
                temprow.append(row[i])
            self.paytable.append(temprow)

        if(self.debug_level >= 2):
            print(f"        Paytable: {self.paytable}")

        # set the RTP
        self.rtp_data = pd.read_excel(self.input_filepath, sheet_name=self.rtp_sheetname)
        self.vi_data = pd.read_excel(self.input_filepath, sheet_name=self.vi_sheetname)
        # this is where the data is pulled from the columns on the rtp sheet
        self.rtp = self.rtp_data[self.rtp_column][0] * 100 ## times 100 so that we have the percentage that matches the data
        self.vi = self.vi_data[self.vi_column][0]

        # Paytable Math begins here. 
        #total_combinations = 0
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
                if(self.debug_level >= 3):
                    print(f"        **** debug: reel pos: {int(reel_pos[0])}")
                symbols.append(self.game_window[int(reel_pos[0])][int(reel_pos[2])])
            if(self.debug_level >= 1):
                print(f"    ****     testing payline {iteration} with symbols: {str(symbols)}     ****")  # this is pulling game window correctly
            #test against paytable

            self.reset_wildsymbols()
            for win_combo in self.paytable:
                if(self.debug_level >= 2):
                    print(f"        - Winning Combo Line being tested: {str(win_combo)}")
                for reelnum in range(0, self.reels):
                    # reworking logic..
                    if(self.debug_level >= 2):
                        print(f"             - testing reel: {str(reelnum+1)} out of {str(self.reels)} for {str(symbols[reelnum])} to match {str(win_combo[reelnum])}")
                    if "*" in str(win_combo[reelnum]):
                        #print("Found an Any Type Symbol")
                        if win_combo[reelnum] == '*B':
                            for sym in ['1B','2B', '3B']:
                            # eventually, logic to include the right ones from the reel.
                                self.wildsymbols.append(sym)
                            #if(self.debug_level >= 3):
                                #print("            - appended Bars to wild symbols")
                        elif win_combo[reelnum] == '*7':
                            for sym in ['B7','R7']:
                                self.wildsymbols.append(sym)
                            #if(self.debug_level >= 3):
                                #print("            - appended 7s to wild symbols")
                        elif win_combo[reelnum] == '*M':
                            for sym in ['M1','M2', 'M3', 'M4']:
                                self.wildsymbols.append(sym)
                            #if(self.debug_level >= 3):
                                #print("            - appended Ms to wild symbols")
                        elif win_combo[reelnum] == '*F':
                            for sym in ['F5','F6','F7', 'F8', 'F9']:
                                self.wildsymbols.append(sym)
                            #if(self.debug_level >= 3):
                                #print("            - appended Fs to wild symbols")
                        #else: 
                            # any symbol.. for 4 and 5 reels to ignore specific spots (allowing different length win lines)
                        #    self.wildsymbols.append('*')
                        #                # other wild symbols would go here. 

                    # win logic          pt 1: for nan on 5 reel paytables              
                    #if(self.debug_level >= 1 and reelnum > 2):
                    #    print(f"    testing reel {reelnum+1} with win_combo[reelnum]: {win_combo[reelnum]}")
                    if(win_combo[reelnum] == "NaN"):
                        if(self.debug_level >= 3):
                            print(f"    !!!!    Found nan    !!!!")
                        # meaning it encountered an empty cell, assume win
                        self.reset_wildsymbols()
                        ### this is where the hit_total is added, should go off for each win_combo found 
                        #self.hit_total += 1
                        if(self.debug_level >= 3):
                            print(f"    +=+=+=+= summation is currently {self.summation} and about to add {(self.mean_pay - (win_combo[len(win_combo)-1] ) ) ** 2}")
                        self.summation += (self.mean_pay - (win_combo[len(win_combo)-1] ) ) ** 2     ##* self.bet) ) ** 2

                        total_win += win_combo[len(win_combo)-1] * self.bet
                        total_win_display = "{:.2f}".format(total_win) 

                        if(self.debug_level >= 1):
                            print(f"    !!!! WIN! awarding {str(win_combo[len(win_combo)-1])} credits, meaning total win is ${total_win_display} and the winning line is : {str(symbols)} !!!!")
                        self.adjust_credits( win_combo[len(win_combo)-1] * self.bet)  ### this should use credits, so bet value x the payline amount

                        if(self.debug_level >= 2):
                            print(f"    +=+=+=+= summation is now {self.summation}, which added: ({self.mean_pay} minus {(win_combo[len(win_combo)-1])}) squared. ")
                        winbreak = 1
                        self.wintoggle = 1
                        #return True
                        self.reset_wildsymbols()    

                    ### NOTE: Winning logic is *HERE* pt 2
                    if((symbols[reelnum] == win_combo[reelnum]) or (symbols[reelnum] in self.wildsymbols)):
                        #if they do not match at any time, return false 
                        if(self.debug_level >= 1 and reelnum > 1):
                            print(f"        Match symbol {symbols[reelnum]} against the paytable symbol {win_combo[reelnum]} on reel number: {str(reelnum+1)} against the winning combo line: {win_combo}") 
                        #payout is the last entry on the win_combo
                        ######## HERE IS WHERE IT's MISSING stuff on 5 reels --- 
                        if(reelnum + 1 == self.reels): # if it's the same all the way down, the whole line is a win
                            self.reset_wildsymbols()
                            # this is where the hit_total is added, should go off for each win_combo found 
                            #self.hit_total += 1
                            if(self.debug_level >= 3):
                                print(f"    +=+=+=+= summation is currently {self.summation} and about to add {(self.mean_pay - (win_combo[len(win_combo)-1] ) ) ** 2}")
                            self.summation += (self.mean_pay - (win_combo[len(win_combo)-1] ) ) ** 2     ##* self.bet) ) ** 2

                            total_win += win_combo[len(win_combo)-1] * self.bet 
                            total_win_display = "{:.2f}".format(total_win) 
                            if(self.debug_level >= 1):
                                print(f"    !!!! WIN! awarding {str(win_combo[len(win_combo)-1])} credits, meaning total win is ${total_win_display} and the winning line is : {str(symbols)} !!!!")
                            self.adjust_credits( win_combo[len(win_combo)-1] * self.bet)  ### this should use credits, so bet value x the payline amount

                            if(self.debug_level >= 2):
                                print(f"    +=+=+=+= summation is now {self.summation}, which added: ({self.mean_pay} minus {(win_combo[len(win_combo)-1])}) squared. ")
                            winbreak = 1
                            self.wintoggle = 1
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
        if(self.wintoggle == 1):
            self.hit_total += 1
            self.wintoggle = 0
            if(self.debug_level >= 1):
                print(f"    ^+^+ ^-^- +1 hit, now {self.hit_total}")

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
