"""
 read sql into pandas dataframe and export to csv
"""

import pypyodbc
import pandas as pd


connection = pypyodbc.connect('Driver={SQL Server};Server=FWSDE;Database=sde_wjt')

SQLCommand = "SELECT cast(hrapx as nvarchar(10)) + '_' + cast(hrapy as nvarchar(10)) " \
             "as id, hrapx, hrapy, lat, lon from pts_cnty"

# read into a pandas dataframe and export to csv
df = pd.read_sql(SQLCommand, connection)
df.to_csv('pts.csv')
df.to_csv('pts2.csv', sep=' ')

connection.close()
