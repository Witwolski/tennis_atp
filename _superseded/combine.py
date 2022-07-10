import os
import pandas as pd


# First, combine all the pages in each Workbook into one sheet
cwd = os.path.abspath('')
files = os.listdir(cwd)
df_toAppend = pd.DataFrame()
for file in files:
    if file.endswith('.xlsx'):
        df_toAppend = pd.concat(pd.read_excel(file, sheet_name=None), ignore_index=True)
        df_toAppend.to_excel(file)


# And then append all the Workbooks into single Excel Workbook sheet

cwd_2 = os.path.abspath('') 
files_2 = os.listdir(cwd_2)  
df_toCombine = pd.DataFrame()
for file_2 in files_2:
    if file_2.endswith('.xlsx'):
        df_toCombine = df_toCombine.append(pd.read_excel(file_2), ignore_index=True) 
        df_toCombine.to_excel('Combined_Excels.xlsx')