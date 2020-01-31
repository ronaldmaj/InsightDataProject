# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 10:18:48 2020

Download the channel statistics for the channels I have so far:

@author: Ronald Maj
"""

import os
import json
import pandas as pd
import yt_cm as cm

insight_dir = os.getcwd()[0:19]+'\\Documents\\GitHub\\InsightDataProject\\'

vids_df = pd.read_csv(
    insight_dir 
    + 'data\\processed\\all_vids_en_df.csv')

chan_ids = list(set(vids_df['ChannelID']))


#with open(insight_dir+'data\\YT_chan_ids.txt','r') as file:
#    manchan_list = [line.rstrip() for line in file]

# Series of all the channel ids:
#chan_ids_all = chan_ids1.append(pd.Series(manchan_list), ignore_index=True)


### Now call the API in order to download the channel statistics
YT_client = cm.set_up_YT_client()

# Create new dataframe to store these video details:
df_chan_info = pd.DataFrame(columns = [
    'ChannelID',
    'title',
    'description',
    'publishedAt',
#    'country',
    'viewCount',
    'commentCount',
    'subscriberCount',
    'videoCount'])

# List of dict keys to extract from the API response later:
snippet_keys = [
    'title',
    'description',
    'publishedAt',
    'thumbnails']
#    'country']

stats_keys = [
    'viewCount',
    'commentCount',
    'subscriberCount',
    'videoCount']

# Run through the videos existing already:
idxs = [i for i in range(50,len(chan_ids),50)]
idxs = idxs + [len(chan_ids)+1]

prior= 0 
for i,idx in enumerate(idxs):
    chan_slice = chan_ids[prior:idx]
    chan_str = ''
    for chanID in chan_slice:
        chan_str = chan_str+','+chanID
    chan_str = chan_str[1:]
    print('Making request '+str(i+1)+ ' of '+str(len(idxs)))
    try: 
        chan_stats = cm.get_channel_stats(YT_client, chan_str)
    except:
        pass
    
    for chan in chan_stats['items']:
        data = {"ChannelID": chan['id']}
        snippet_data = {key: chan['snippet'][key] for key in snippet_keys}
        stats_data = {key: chan['statistics'][key] for key in stats_keys}
        data.update(snippet_data)
        data.update(stats_data)
        df_chan_info = df_chan_info.append(data,ignore_index=True)

    json_txt = json.dumps(chan_stats)
    if not os.listdir(insight_dir+'data\\raw\\channels\\statistics\\'):
        with open(
                insight_dir
                +'data\\raw\\channels\\statistics\\' 
                + 'channel_stats_json_1'
                + '.json','w') as file:
            file.write(json_txt)
    else:
        with open(
             insight_dir
             +'data\\raw\\channels\\statistics\\' 
             + 'channel_stats_json_' + str(len(os.listdir(insight_dir+'data\\raw\\channels\\statistics\\'))+1)
             + '.json','w') as file:
         file.write(json_txt)
  
    prior = idx
    df_chan_info.to_csv(insight_dir 
    + 'data\\processed\\all_channels_info.csv')