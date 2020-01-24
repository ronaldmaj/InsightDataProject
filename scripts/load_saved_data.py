# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 17:17:20 2020

Load the existing comment data and tables

@author: Ronald Maj
"""
import os
import pandas as pd

insight_dir = os.getcwd()[0:19]+'\\Documents\\GitHub\\InsightDataProject\\'

comms_df = pd.read_csv(insight_dir+'data\\processed\\comments_df.csv', index_col=0)
vids_df = pd.read_csv(insight_dir+'data\\processed\\videos_top30_df.csv', index_col=0)
channels_df = pd.read_csv(insight_dir+'data\\processed\\channels_top50_df.csv', index_col=0)

# Just take one channel as a test
test_cid = channels_df.iloc[1]['ChannelID']
test_vids_list = list(vids_df[vids_df['ChannelID'] == test_cid]['VidID'])

# Get just the comments from the test case
test_df = comms_df[comms_df['videoId'].isin(test_vids_list)]

