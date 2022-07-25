#dataframetest.py

import pandas as pd

input_filepath = "./PARishSheets.xlsx"
payline_data = pd.read_excel(input_filepath, sheet_name='Paylines9')

paylines = []
for idx, row in payline_data.iterrows():

    # for each row
    temprow = [] 
    for i in range(0, payline_data.shape[1]):
        temprow.append(row[i])
    paylines.append(temprow)
print(paylines)

paylines_baseline=[
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

#print("and baseline")
#print(paylines_baseline)

# this is it: payline[payline_row][payline entry][reel=0,position=1]
print(f"{paylines[0][2][0]}")
###
