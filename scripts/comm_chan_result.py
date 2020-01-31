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

insight_dir = 'C:\\Users\\Ronald Maj\\Documents\\GitHub\\InsightDataProject\\'

chan_info_df = pd.read_csv(insight_dir + 'data\\cleaned\\all_channels_info.csv', index_col=0)
vids_df = pd.read_csv(insight_dir+'data\\cleaned\\all_videos_dup_na_clean_df.csv', index_col=0)
comms_df = pd.read_csv(insight_dir+'data\\cleaned\\all_comments_dup_na_clean_df.csv', index_col=0)

nlp = spacy.load("en_core_web_lg")

database_mat = np.load('C:\\Users\\Ronald Maj\\Documents\\GitHub\\YT_Comment_Analytics\\comms_mat_all.npy')

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
    comm_count = comm_count.most_common()
    
    chan_dict_list= [len(comm_count)]
    
    for chan_id in comm_count.keys():
        chan_result = results_info_df[results_info_df['ChannelID'] == chan_id].iloc[0]
        chan_result_dict = {
            'Channel Name':chan_result['title'],
            'Comment Fraction':round(comm_count[chan_id]/sum(comm_count.values()),2),
            'No. Subscribers':chan_result['subscriberCount'],
            'No. Views':chan_result['viewCount_chan'],
            'Likes/Views (on video)':chan_result['likeCount'] / chan_result['viewCount_vid'],
            'Comments/Views (on video)':chan_result['commentCount_vid'] / chan_result['viewCount_vid']
            }
        chan_dict_list.append(chan_result_dict)
    
    comm_dict_list= [len(results_info_df)]
    
    for i in results_info_df.index:
        comm_result_dict = {
        'Name':results_info_df.iloc[i]['authorDisplayName'],
        'Comment':results_info_df.iloc[i]['textDisplay'],
        'Sim Score':round(results_info_df.iloc[i]['sim_score'],2),
        'Profile Pic':results_info_df.iloc[i]['authorProfileImageUrl']          
            }
        comm_dict_list.append(comm_result_dict)

    return chan_dict_list, comm_dict_list


