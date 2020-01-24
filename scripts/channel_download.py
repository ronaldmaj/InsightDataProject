# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 00:40:41 2020

Try to get the loyal / regular commentors and their contribution

@author: Ronald Maj
"""

import os
import time
import googleapiclient.discovery
import pandas as pd
import yt_cm as cm
import json
#%%
insight_dir = os.getcwd()[0:19]+'\\Documents\\GitHub\\InsightDataProject\\'

# Set up the Youtube client, search for the top 50 results for 'vlog' and
# extract the channel Ids into a dataframe: 

YT_client = cm.set_up_YT_client()

#%%
def search_results(YT_client,query,pg_tok=None):

    request = YT_client.search().list(
        part="snippet",
        maxResults=50,
        pageToken = pg_tok,
        publishedBefore="2020-01-01T00:00:00Z",
        q=query,
        type="channel",
        order='relevance',
        relevanceLanguage ='en'
    )
    response = request.execute()
    time.sleep(0.3)
    return response

#%%

channels_df = pd.read_csv(insight_dir+'data\\processed\\channels_top50_df.csv',index_col=0)

nxt_pg = 'CDIQAA'

for i in range(0,8):
    channels2 = search_results(YT_client, 'vlog', nxt_pg)
    top_vlogs = channels2['items']

    channel_info = {
    'ChannelTitle':[vlog['snippet']['title'] for vlog in top_vlogs],
    'ChannelID':[vlog['snippet']['channelId'] for vlog in top_vlogs],
    'ChannelDescription':[vlog['snippet']['description'] for vlog in top_vlogs]
    }    
    
    channels_df_new = pd.DataFrame.from_dict(channel_info)
    channels_df = channels_df.append(channels_df_new).reset_index().drop('index',axis=1)
    
    nxt_pg = channels2['nextPageToken']
    
    json_txt = json.dumps(channels2)
    with open(
          insight_dir
          +'data\\raw\\channels\\' 
          + 'channels_json_' + str(len(os.listdir(insight_dir+'data\\raw\\channels\\'))+1)
          + '.json','w') as file:
        file.write(json_txt)
    
    


