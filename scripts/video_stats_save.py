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

# Most recent video csv:
vids_csv_loc = insight_dir + 'data\\processed\\videos_manulist_df.csv'
# vids_csv_out = insight_dir + 'data\\processed\\videos_top30_df.csv'

def download_save_video_stats(vids_csv_file):
    print('Loading .csv file')
    df_vids = pd.read_csv(vids_csv_file, index_col=0)
    
    # Set up the Youtube client, search for the top 50 results for 'vlog' and
    # extract the channel Ids into a dataframe: 
    
    YT_client = cm.set_up_YT_client()
    
    # Create new dataframe to store these video details:
    df_vid_stats = pd.DataFrame(columns = ['VidID',
        'viewCount',
        'likeCount',
        'dislikeCount',
        'favoriteCount',
        'commentCount'])
    
    # Run through the videos existing already:
    idxs = [i for i in range(50,len(df_vids),50)]
    prior= 0 
    for i,idx in enumerate(idxs):
        vid_list = list(df_vids[prior:idx]['VidID'].values)
        vid_str = ''
        for vidID in vid_list:
            vid_str = vid_str+','+vidID
        vid_str = vid_str[1:]
        print('Making request '+str(i+1)+ ' of '+str(len(idxs)))
        try: 
            vid_stats = cm.get_video_stats(YT_client, vid_str)
        except:
            pass
        
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
    
    vid_list = list(df_vids[prior:]['VidID'].values)
    vid_str = ''
    for vidID in vid_list:
        vid_str = vid_str+','+vidID
    vid_str = vid_str[1:]
    try:
        vid_stats = cm.get_video_stats(YT_client, vid_str)
    except:
        pass
    
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
     
    df_vids = df_vids.join(df_vid_stats.set_index('VidID'), on='VidID')
    df_vids.to_csv(vids_csv_file)
    
download_save_video_stats(vids_csv_loc)
