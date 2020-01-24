# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 02:10:29 2020

Run the youtube api once more to get the video statistics

@author: Ronald Maj
"""

import os
#import time
#import googleapiclient.discovery
import pandas as pd
import yt_cm as cm
import json
#%%
insight_dir = os.getcwd()[0:19]+'\\Documents\\GitHub\\InsightDataProject\\'

vids_df = pd.read_csv(insight_dir+'data\\processed\\videos_top30_df.csv', index_col=0)

# Set up the Youtube client, search for the top 50 results for 'vlog' and
# extract the channel Ids into a dataframe: 

YT_client = cm.set_up_YT_client()

#%%

# Create new dataframe to store these video details:
df_vid_stats = pd.DataFrame(columns = ['VidID',
    'viewCount',
    'likeCount',
    'dislikeCount',
    'favoriteCount',
    'commentCount'])

# Run through the videos existing already:
idxs = [i for i in range(50,1260,50)]
prior= 0 
for i,idx in enumerate(idxs):
    print('Getting '+str(i)+' of '+str(len(idxs)))
    vid_list = list(vids_df[prior:idx]['VidID'].values)
    vid_str = ''
    for vidID in vid_list:
        vid_str = vid_str+','+vidID
    vid_str = vid_str[1:]
    vid_stats = cm.get_video_stats(YT_client, vid_str)
    
    for vid in vid_stats['items']:
        data = {"VidID": vid['id']}
        data.update(vid['statistics'])
        df_vid_stats = df_vid_stats.append(data,ignore_index=True)
    
    json_txt = json.dumps(vid_stats)
    if not os.listdir(insight_dir+'data\\raw\\videos\\statistics\\'):
        with open(
                insight_dir
                +'data\\raw\\videos\\statistics\\' 
                + 'videostats_json_1'
                + '.json','w') as file:
            file.write(json_txt)
    else:
        with open(
             insight_dir
             +'data\\raw\\videos\\statistics\\' 
             + 'videostats_json_' + str(len(os.listdir(insight_dir+'data\\raw\\videos\\statistics\\'))+1)
             + '.json','w') as file:
         file.write(json_txt) 
  
    prior = idx

vid_list = list(vids_df[prior:]['VidID'].values)
vid_str = ''
for vidID in vid_list:
    vid_str = vid_str+','+vidID
vid_str = vid_str[1:]
vid_stats = cm.get_video_stats(YT_client, vid_str)

for vid in vid_stats['items']:
    data = {"VidID": vid['id']}
    data.update(vid['statistics'])
    df_vid_stats = df_vid_stats.append(data,ignore_index=True)

json_txt = json.dumps(vid_stats)

with open(
     insight_dir
     +'data\\raw\\videos\\statistics\\' 
     + 'videostats_json_' + str(len(os.listdir(insight_dir+'data\\raw\\videos\\statistics\\'))+1)
     + '.json','w') as file:
 file.write(json_txt) 
 
vids_df = vids_df.join(df_vid_stats.set_index('VidID'), on='VidID')
vids_df.to_csv(insight_dir+'data\\processed\\videos_top30_df.csv')
