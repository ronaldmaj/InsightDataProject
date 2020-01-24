# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 12:22:06 2020

Script to scrape comments from the top 50 results for the term 'vlog'

@author: Ronald Maj
"""
#%%
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
def channel_seach_call(YT_client, query):

    top_vlogs_search = cm.search_results(YT_client,'vlog')
    
    json_txt = json.dumps(top_vlogs_search)
    if not os.listdir(insight_dir+'data\\raw\\channels\\'):
        with open(
                insight_dir
                +'data\\raw\\channels\\' 
                + 'channels_json_1'
                + '.json','w') as file:
            file.write(json_txt)
    else:
        with open(
             insight_dir
             +'data\\raw\\channels\\' 
             + 'channels_json_' + str(len(os.listdir(insight_dir+'data\\raw\\channels\\'))+1)
             + '.json','w') as file:
         file.write(json_txt) 
    return top_vlogs_search

top_vlogs_search = channel_seach_call(YT_client,'vlog')
top_vlogs = top_vlogs_search['items']

channel_info = {
    'ChannelTitle':[vlog['snippet']['title'] for vlog in top_vlogs],
    'ChannelID':[vlog['snippet']['channelId'] for vlog in top_vlogs],
    'ChannelDescription':[vlog['snippet']['description'] for vlog in top_vlogs]
    }

channels_df = pd.DataFrame.from_dict(channel_info)

#channels_df.to_csv(insight_dir+'data\\processed\\channels_top50_df.csv')

#%%

# For each of the channels, get the most recent 30 videos from the channel and
# save in dataframe

vids_df = pd.DataFrame(
    columns=['VidID',
             'ChannelID',
             'VidTitle',
             'VidDescription',
             'VidPublished'])

def videos_of_channel_call(YT_client, channel_id):

    vids_dict = cm.get_videos_of_channel(YT_client, channel_id)
    
    json_txt = json.dumps(vids_dict)
    if not os.listdir(insight_dir+'data\\raw\\videos\\'):
        with open(
                insight_dir
                +'data\\raw\\videos\\' 
                + 'videos_json_1'
                + '.json','w') as file:
            file.write(json_txt)
    else:
        with open(
             insight_dir
             +'data\\raw\\videos\\' 
             + 'videos_json_' + str(len(os.listdir(insight_dir+'data\\raw\\videos\\'))+1)
             + '.json','w') as file:
         file.write(json_txt) 
    return vids_dict

for c_id in channels_df['ChannelID'][49:]:
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

#vids_df.to_csv(insight_dir+'data\\processed\\videos_top30_df.csv')

df_comms_list = []

#%%

#if lastest_vid:
#    strt = vids_df[vids_df['VidID'] == lastest_vid].index[0]
#else:
strt = -1

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
    if not os.listdir(insight_dir+'data\\raw\\comments\\'):
        with open(
                insight_dir
                +'data\\raw\\comments\\' 
                + 'comments_json_1'
                + '.json','w') as file:
            file.write(json_txt)
    else:
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
    
comms_df.to_csv(insight_dir+'data\\processed\\comments_df3.csv')
