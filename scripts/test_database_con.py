# -*- coding: utf-8 -*-
"""
Created on Sun Feb  9 20:22:19 2020

Quick test of the new tables in the database containing channel, vid, comm data

@author: Ronald Maj
"""

# Test script for the trial of connection to a PostgreSQL database
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

import pandas as pd

# Create a connection to my database: test_db
connect_str = 'postgresql://poweruser:insight2020@localhost/test_db' 
engine = create_engine(connect_str, poolclass=NullPool)

# Create test query
convar = engine.connect() 
rsvar = convar.execute('SELECT title FROM chans_table WHERE "subscriberCount" > 20000000') 

#example of creating a dataframe 
df = pd.DataFrame(rsvar.fetchall())
df.columns = rsvar.keys() 

print(df.head())
convar.close 