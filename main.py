# main.py

from classes.tkGui import *

if __name__ == '__main__':
    """ main class: take input and call the GUI, which contains the simulator. """
    # GUI call here - this handles everything else, since it's ui / button driven 
    sim_gui = tkGui()
    sim_gui.mainloop()
    # this is what needs to get 'built' / run by python