# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 00:51:43 2020

Take in a list of channels to get:
    - the 30 most recent video_id and information about that
    - the top 200 comments from those videos

@author: Ronald Maj
"""

import os
import pandas as pd
import yt_cm as cm
import json

# Function to get the videos of a given channel plus save raw json files
def videos_of_channel_call(YT_client, channel_id):

    vids_dict = cm.get_videos_of_channel(YT_client, channel_id)
    
    json_txt = json.dumps(vids_dict)
    with open(
         insight_dir
         +'data\\raw\\videos\\' 
         + 'videos_json_' + str(len(os.listdir(insight_dir+'data\\raw\\videos\\'))+1)
         + '.json','w') as file:
     file.write(json_txt) 
    return vids_dict

# Set up the Youtube client
YT_client = cm.set_up_YT_client()

# Directory to list of channels
insight_dir = os.getcwd()[0:19]+'\\Documents\\GitHub\\InsightDataProject\\'
# Open up file and read the lines:
with open(insight_dir+'data\\YT_chan_ids.txt','r') as file:
    yt_channels = [line.rstrip() for line in file]

# For each of the channels, get the most recent 30 videos from the channel and
# save in dataframe

vids_df = pd.DataFrame(
    columns=['VidID',
             'ChannelID',
             'VidTitle',
             'VidDescription',
             'VidPublished'])

for c_id in yt_channels:
    last_c = c_id
    vids_dict = videos_of_channel_call(YT_client, c_id)
    vids_list = vids_dict['items']
    # Only keep channels that have more than 30 videos
    if len(vids_list) < 30:
        continue
    else:
        for vid in vids_list[0:30]:
            vid_dict = {'VidID':vid['snippet']['resourceId']['videoId'],
                        'ChannelID':vid['snippet']['channelId'],
                        'VidTitle':vid['snippet']['title'],
                        'VidDescription':vid['snippet']['description'],
                        'VidPublished':vid['snippet']['publishedAt']
                }
            vids_df = vids_df.append(vid_dict, ignore_index=True)
            
#vids_df.to_csv(insight_dir+'data\\processed\\videos_manulist_df.csv')

#%%

# Download comments now

#df_comms_list = []

#if lastest_vid:
#strt = vids_df[vids_df['VidID'] == lastest_vid].index[0]
#else:
#strt = -1

# Now for each video, need to get the comments.
for v_id in vids_df['VidID'][strt+1:]:
    lastest_vid = v_id
    vid_num_str = str(vids_df[vids_df['VidID'] == lastest_vid].index[0])
    num_vids_str = str(len(vids_df['VidID']))
    print('Fetching comments for video '+vid_num_str+' of '+num_vids_str)
    try:
        comm_pg1 = cm.get_comments_page(YT_client,
                                        v_id, 
                                        'relevance',
                                        pagetok=None)
            
        comm_pg2 = cm.get_comments_page(YT_client,
                                        v_id, 
                                        'relevance',
                                        pagetok=comm_pg1['nextPageToken'])
    except:
        continue
    
    
    json_txt = json.dumps(comm_pg1)
    with open(
         insight_dir
         +'data\\raw\\comments\\' 
         + 'comments_json_' + str(len(os.listdir(insight_dir+'data\\raw\\comments\\'))+1)
         + '.json','w') as file:
        file.write(json_txt)
    
    
    json_txt = json.dumps(comm_pg2)
    with open(
        insight_dir
        +'data\\raw\\comments\\' 
        + 'comments_json_' + str(len(os.listdir(insight_dir+'data\\raw\\comments\\'))+1)
        + '.json','w') as file:
        file.write(json_txt)   

    thread_list = comm_pg1["items"] + comm_pg2['items']

    # Create Dataframe from the comment dictionary that results
    cols = ['CommID'] + list(thread_list[0]['snippet']["topLevelComment"]['snippet'].keys()) + ['parentId']
    df_comms = pd.DataFrame(columns=cols)

    for item in thread_list:
        data = {"CommID": item['id'], 'parentId': 0}
        data.update(item['snippet']["topLevelComment"]['snippet'])
        df_comms = df_comms.append(data,ignore_index=True)
        if 'replies' in item.keys():
            for reply in item['replies']['comments']:
                data = {"CommID": reply['id']}
                data.update(reply['snippet'])
                df_comms = df_comms.append(data,ignore_index=True)
    df_comms_list.append(df_comms)

#if comms_df.empty:
comms_df = pd.DataFrame(columns=df_comms_list[0].columns)
#else:
#    pass

for df in df_comms_list:
    comms_df = comms_df.append(df, ignore_index=True)
    
comms_df.to_csv(insight_dir+'data\\processed\\comments_df5.csv')


