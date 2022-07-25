#dataframetest2.py

import pandas as pd

input_filepath = "./PARishSheets.xlsx"
paytable_data = pd.read_excel(input_filepath, sheet_name='Paytable3')

paytable = []

for idx, row in paytable_data.iterrows():
    # for each row
    temprow = [] 
    for i in range(0, paytable_data.shape[1]):
        temprow.append(row[i])
    paytable.append(temprow)
print(paytable)


paytable_baseline = [
    ('W','W','W',12.5),
    ('B7','B7','B7',11.25),
    ('R7','R7','R7',10.75),
    ('*7','*7','*7',10),
    ('3B','3B','3B',6.50),
    ('2B','2B','2B',6),
    ('1B','1B','1B',5.5),
    ('*B','*B','*B',3)
]
print(paytable_baseline)

print(len(paytable))