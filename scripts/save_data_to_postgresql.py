# -*- coding: utf-8 -*-
"""
Created on Sun Feb  9 17:38:20 2020

Creating PostgreSQL tables in database from the .csv files containing comments, 
video and channel data

@author: Ronald Maj
"""

# Test script for the trial of connection to a PostgreSQL database
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

import pandas as pd

# Create a connection to my database: test_db
connect_str = 'postgresql://poweruser:insight2020@localhost/test_db' 
engine = create_engine(connect_str, poolclass=NullPool)

# Load relevant csv files (channel, video, comments)
chan_info_df = pd.read_csv('all_channels_info.csv', index_col=0)
vids_df = pd.read_csv('all_videos_dup_na_clean_df.csv', index_col=0)
comms_df = pd.read_csv('all_comments_dup_na_clean_df.csv', index_col=0)

# Do all the renaming of columns:
# Need to rename the columns where there is ambiguity or no overlap on ID (eg 
# on 'videoId' vs 'VidID' column names)
cols = list(comms_df.columns)
cols[-2] = 'VidID'
cols[9] = 'publishedAt_comm'
comms_df.columns = cols

cols = list(vids_df.columns)
cols[5] = 'viewCount_vid'
cols[-1] = 'commentCount_vid'
vids_df.columns = cols

cols = list(chan_info_df.columns)
cols[4] = 'viewCount_chan'
cols[5] = 'commentCount_chan'
chan_info_df.columns = cols

comms_df = comms_df.reset_index(drop=True)

# Push the dataframes up to the test_db database:
comms_df.to_sql('comms_table',
                  con=engine, 
                  index=True, 
                  chunksize=10000)

vids_df.to_sql('vids_table',
                  con=engine, 
                  index=False, 
                  chunksize=1000)

chan_info_df.to_sql('chans_table',
                  con=engine, 
                  index=False)


## If you want to connect remotely, use this instead: DATABASEURL=postgres://{user}:{password}@{hostname}:{port}/{database-name}

## Where hostname can be the elastic ip or if using AWS, it is the public DNS like:
## ec2-54-216-22-100.eu-west-1.compute.amazonaws.com

## Port will be = 5432