# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 21:24:32 2020

Function for generating the comment / channel outputs after a user input 

@author: Ronald Maj
"""

#import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
import pandas as pd
import numpy as np
import spacy
import json
from glob import glob

chan_info_df = pd.read_csv('all_channels_info.csv', index_col=0)
vids_df = pd.read_csv('all_videos_dup_na_clean_df.csv', index_col=0)
comms_df = pd.read_csv('all_comments_dup_na_clean_df.csv', index_col=0)

nlp = spacy.load("en_core_web_lg")


# Load the database of sentence embeddings:
array_parts = []

part_locs = glob('*.npy')
part_locs = sorted(part_locs)

for loc in part_locs:
	part = np.load(loc)
	array_parts.append(part)

database_mat = np.concatenate(array_parts)

# Turning large numbers into 'human' form
def human_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])


def get_comment_channel_results(search_term, sim_thresh):
    #### Put in search term of interest:
    
    search_doc = nlp(search_term)
    
    # Get the vector representation:
    search_vec = search_doc.vector.reshape(1,-1)
    
    #### Create similarity vector
    sim_vec = cosine_similarity(search_vec,database_mat)
    
    ####  Return ordered list of comments based on threshold:
    tf_ar = sim_vec > sim_thresh
     
    # Create a results_info_df that collects all the relevant information on 
    # the resultant list produced:
    results_info_df = comms_df[tf_ar[0]][['CommID',
                                               'authorChannelUrl',
                                               'authorDisplayName',
                                               'authorProfileImageUrl',
                                               'parentId',
                                               'publishedAt',
                                               'textDisplay',
                                               'videoId']].copy(deep=True)
    
    # Assign a new column in the results_info dataframe to associate the similarity score with the correct comment and sort:
    results_info_df['sim_score'] = sim_vec[0][tf_ar[0]]
    results_info_df.sort_values(by='sim_score',ascending=False, inplace=True)
    
    #### Need to rename the column with the video ID to match up with that in the vids_df
    cols = list(results_info_df.columns)
    cols[-2] = 'VidID'
    results_info_df.columns = cols
    results_info_df = results_info_df.merge(
        right=vids_df,
        how='left',
        on='VidID',
        suffixes=('_comm', '_vid'))
    
    #### Lastly get the channel info:
    
    # Rename common columns:
    cols = list(results_info_df.columns)    
    cols[5] = 'publishedAt_comm'    
    results_info_df.columns = cols    
    results_info_df = results_info_df.merge(
        right=chan_info_df,
        how='left',
        on='ChannelID',
        suffixes=('_vid', '_chan'))
    
    comm_count = Counter(results_info_df['ChannelID'])
    comm_count_list = comm_count.most_common()
    
    chan_dict_list= [human_format(len(comm_count))]
    
    
    # Send the relevant info to the website:
	
    for chan_id,count in comm_count_list[0:6]:
        chan_result = results_info_df[results_info_df['ChannelID'] == chan_id].iloc[0]
        thumb_dict_str = chan_result['thumbnails']
        thumb_dict_str = thumb_dict_str.replace("\'", "\"")
        thumb_dict = json.loads(thumb_dict_str)
        prof_pic_url = thumb_dict['default']['url']
        chan_result_dict = {
            'Channel Name':chan_result['title'],
            'Chan_url':'https://www.youtube.com/channel/'+chan_id,
            'Comment Fraction':human_format(count),
            'No. Subscribers':human_format(chan_result['subscriberCount']),
            'No. Views':human_format(chan_result['viewCount_chan']),
            'Likes/Views (on video)':round(chan_result['likeCount'] / chan_result['viewCount_vid'],5),
            'Comments/Views (on video)':round(chan_result['commentCount_vid'] / chan_result['viewCount_vid'],5),
            'Chan Profile Pic':prof_pic_url
            }
        chan_dict_list.append(chan_result_dict)
    
    comm_dict_list= [len(results_info_df)]
    
    for i in results_info_df[0:6].index:
        comm_result_dict = {
        'Name':results_info_df.iloc[i]['authorDisplayName'],
        'Comment':results_info_df.iloc[i]['textDisplay'],
        'Sim Score':round(results_info_df.iloc[i]['sim_score'],2),
        'Profile Pic':results_info_df.iloc[i]['authorProfileImageUrl'],
        'Vid_url':'https://www.youtube.com/watch?v='+results_info_df.iloc[i]['VidID'],
        'Vid_title':results_info_df.iloc[i]['VidTitle'],
        'Channel Name':results_info_df.iloc[i]['title'],
        'Chan_url':'https://www.youtube.com/channel/'+results_info_df.iloc[i]['ChannelID']        
            }
        comm_dict_list.append(comm_result_dict)

    return chan_dict_list, comm_dict_list


