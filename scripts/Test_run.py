# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 12:22:06 2020

Script to scrape comments from the top 50 results for the term 'vlog'

@author: Ronald Maj
"""

import os
import time
import googleapiclient.discovery
import pandas as pd
import yt_cm as cm

# Set up the Youtube client, search for the top 50 results for 'vlog' and
# extract the channel Ids into a dataframe: 

YT_client = cm.set_up_YT_client()
top_vlogs_search = cm.search_results(YT_client,'vlog')
top_vlogs = top_vlogs_search['items']

channel_info = {
    'ChannelTitle':[vlog['snippet']['title'] for vlog in top_vlogs],
    'ChannelID':[vlog['snippet']['channelId'] for vlog in top_vlogs],
    'ChannelDescription':[vlog['snippet']['description'] for vlog in top_vlogs]
    }

channels_df = pd.DataFrame.from_dict(channel_info)

# For each of the channels, get the most recent 30 videos from the channel and
# save in dataframe

vids_df = pd.DataFrame(
    columns=['VidID',
             'ChannelID',
             'VidTitle',
             'VidDescription',
             'VidPublished'])

for c_id in channels_df['ChannelID']:
    vids_dict = cm.get_videos_of_channel(YT_client, c_id)
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
            vids_df = vids_df.append(vid_dict , ignore_index=True)
    
# Now for each video, I will need to get the comments.

vid_ID = vids_df['VidID'][10]

comm_pg1 = cm.get_comments_page(YT_client,
                                vid_ID, 
                                'relevance',
                                pagetok=None)

comm_pg2 = cm.get_comments_page(YT_client,
                                vid_ID, 
                                'relevance',
                                pagetok=comm_pg1['nextPageToken'])


    
    


