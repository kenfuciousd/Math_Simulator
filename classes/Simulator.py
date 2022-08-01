from collections import defaultdict
import pandas as pd     # for reading Excel
import matplotlib.pyplot as plt  # for displaying math

class Simulator():
    """ simulator class: takes in the SlotMachine class object, does stuff and tracks it. """
    def __init__(self, sm, simnum, debug_level):
        self.simnum = simnum
        self.sm = sm
        self.this_bet = sm.bet * float(sm.paylines_total)
        self.incremental_credits = []
        self.incremental_rtp = []
        self.spins = []
        self.df_dict = ["credits"] # takes up the header line and lets us start at iteration 1 for data purposes
        self.rtp_dict = ["RTP"] # takes up the header line and lets us start at iteration 1 for data purposes
        self.debug_level = debug_level
        self.total_bet = 0
        self.total_won = 0
        self.plot_toggle = 0 
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
                self.total_bet += self.this_bet 
                if(self.debug_level >= 1):
                    print(f"spin {str(iteration+1)} and credits ${str(self.sm.return_credits())}")
                self.sm.spin_reels()
                self.total_won += self.sm.this_win 
                self.incremental_rtp.append( (self.total_won / self.total_bet) * 100 )
                self.incremental_credits.append(self.sm.return_credits())
                self.spins.append(iteration+1)
                self.rtp_dict.insert(iteration+1, (self.total_won / self.total_bet))
                self.df_dict.insert(iteration+1, self.sm.this_win)

                if(self.debug_level >= 3):
                    print(f"    spin {str(iteration)} and credits ${str(self.sm.return_credits())} and added to the dictionary: {self.df_dict[iteration]}")

    def plot_credits_result(self):
        #plt.style.use('_mpl-gallery')
        if(self.plot_toggle == 0):
            #plt.clf()
            self.plot_toggle = 2
        if(self.plot_toggle == 1):
            plt.clf()
            self.plot_toggle = 2
        plt.ylabel('Credits')
        plt.xlabel('Spins')
        plt.xlim(-1,self.simnum) # show total expected spins. 
        plt.plot(self.spins, self.incremental_credits)
        plt.show()

    def plot_rtp_result(self):
        rtp = []
        if(self.plot_toggle == 0):
            #plt.clf()
            self.plot_toggle = 1
        if(self.plot_toggle == 2):
            plt.clf()
            self.plot_toggle = 1
        plt.ylabel('Return To Player %')
        plt.xlabel('Spins')
        plt.xlim(-1,self.simnum) # show total expected spins. 
        plt.plot(self.spins, self.incremental_rtp)
        #print(f'debug plot: rtp is {self.sm.rtp}')
        for i in range(0, len(self.spins)):
            rtp.append(self.sm.rtp)
        plt.plot(self.spins, rtp, linestyle = 'dashed', color='magenta')
        plt.text(self.spins[len(self.spins)-1] - 160, self.sm.rtp + 5, "Expected RTP " + str(rtp[0]) + "%", color='magenta')
        plt.show()       

    # this should be used, in some form.. I don't like addressing this directly. However 
    #def return_dataframe(self):
    #    print(f" ... looking at {str(self.df_dict)}")
    #    return pd.DataFrame(self.df_dict)
