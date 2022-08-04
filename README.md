# Math_Simulator
Version 2 of a current project, broken out into its own repository

This is a Math Simulator project, meant to take in excel .xslx files with correct formatting, and build a virtual slot machine (3 or 5 reel, 3 positions exposed) based on those parameters in order to simulate the behavior over time, and measure the mathematics behind it. 

Required: Python3, installed Anaconda package

To begin, run the main.py file through the python compiler.  
(command prompt: python main.py )
There are no additional arguments to add. 



Input guidelines for the Excel file are included in the .pdf, and in the example PARishSheet.xslx file.  The formatting is as follows:

The excel file needs 4 sheets: 'Reels', 'Paytable', 'Paylines', 'RTP'

'Reels' sheet should have the Reel Strips, with no spaces, labeled "Reel #"

'Paytable' sheet should have the paytable sequence from largest to smallest, with the reel symbols listed and the pay line amount as the final column. note: for 5 reel, blanks are allowed in reel positions 4 or 5, to allow for smaller pay line wins. 

'Paylines' should be two numbers per cell: reel,position. Important: Counting starts at 0; so 0,0 is the uppermost left game widow position, 0,1 is the second position on the first reel; 2,2 is the third position on the third reel. 

'RTP' sheet should have at least two columns, one labeled "Volatility" with the calculated volatility index, and "RTP" for the calculated Return To Player percentage. 



Next development steps: 
1. more, robust error checking for each of the inputs. 
2. solidifying the plotting behavior from matplotlib. one request, to be able to compare the plots of multiple simulator runs. "It works on my machine."
3. broadening inputs? allowing other methods of building the reels, paytable, paylines, etc? through other file types? or a UI?
4. Additional win behaviors: 'scatter' symbol type, and 'bonus' wins awarded from an exterior source or server
5. Additional input flexibility to allow for different game window configurations outside 3x3 and 5x3
