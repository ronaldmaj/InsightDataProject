# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 21:24:32 2020

Function for generating the comment / channel outputs after a user input 

@author: Ronald Maj
"""

#import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
import spacy
import json
from glob import glob
from itertools import islice

# PostgreSQL database
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

# Create a connection to my database: test_db
connect_str = 'postgresql://poweruser:insight2020@localhost/test_db' 
engine = create_engine(connect_str, poolclass=NullPool)

# Load relevant information (channel, video, comments)
#chan_info_df = pd.read_csv('all_channels_info.csv', index_col=0)
#vids_df = pd.read_csv('all_videos_dup_na_clean_df.csv', index_col=0)
#comms_df = pd.read_csv('all_comments_dup_na_clean_df.csv', index_col=0)

# Start NLP model to put search term through
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
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'),
	['', 'K', 'M', 'B', 'T'][magnitude])


def take(n, iterable):
    # Return first n items of the iterable as a list
    return list(islice(iterable, n))


def create_comm_list(results_info_df, num_disp):
    # Comment list for output back to the website
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
    
    return comm_dict_list

def create_chan_list(sim_sum_sorted_dict, results_info_df, num_disp):
    # Channel list for output back to the website
    top_chans = take(num_disp, sim_sum_sorted_dict.items())
    
    chan_dict_list= [human_format(len(sim_sum_sorted_dict))]
    
    # Create the dict for channel details to send to website:
    for chan_id,count in top_chans:
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
    
    return chan_dict_list


def get_comment_channel_results(search_term, num_comms):
    #### Put in search term of interest:
    search_doc = nlp(search_term)
    
    # Get the vector representation:
    search_vec = search_doc.vector.reshape(1,-1)
    
    #### Create similarity vector
    sim_vec = cosine_similarity(search_vec,database_mat)
    
    # Create a dataframe out of it in order to get top 'num_comms' of the 
    # comments
    sim_df = pd.DataFrame(sim_vec[0],columns=['sim_score'])
    sim_df.index.name = 'index'
    
    ordered_sims_df = sim_df.sort_values(by='sim_score',ascending=False)
    top_comms_idxs = list(ordered_sims_df.head(num_comms).index)
    
    
    
    # Query to create table out of the relevant comments:
    convar = engine.connect()
    
    idx_query_list = ", ".join( repr(idx) for idx in top_comms_idxs)
    relevant_comms_cols = '\
    "index",\
    "CommID",\
    "VidID",\
    "ChannelID",\
    "thumbnails",\
    "authorDisplayName",\
    "textDisplay",\
    "authorProfileImageUrl",\
    "VidTitle",\
    "title",\
    "subscriberCount",\
    "viewCount_chan",\
    "likeCount",\
    "dislikeCount",\
    "viewCount_vid",\
    "publishedAt",\
    "pblishedAt_comm"\
    '
    s_query = f'SELECT {relevant_comms_cols} \
                FROM comms_table LEFT JOIN vids_table USING("VidID") \
                    LEFT JOIN chans_table USING("ChannelID") \
                WHERE "index" IN ({idx_query_list})'
        
    rsvar = convar.execute(s_query)
    
    #  Create a dataframe out of the resultant table
    results_info_df = pd.DataFrame(rsvar.fetchall())
    results_info_df.columns = rsvar.keys()
    
    # Add new column to 
    results_info_df = results_info_df.join(ordered_sims_df.head(num_comms))
    
    ###########################################################################
    
    # Assign the scores to the dataframe and sort by the similarity scores
#    comms_df['sim_score'] = (sim_vec[0])

    
#    rel_comms_df = comms_df.sort_values(by='sim_score',ascending=False).head(num_comms)
     
    # Create a results_info_df that collects all the relevant information on 
    # the resultant df:
#    results_info_df = rel_comms_df[[
#                                    'CommID',
#                                    'authorChannelUrl',
#                                    'authorDisplayName',
#                                    'authorProfileImageUrl',
#                                    'parentId',
#                                    'publishedAt',
#                                    'textDisplay',
#                                    'videoId',
#                                    'sim_score']].copy(deep=True)
    
    #### Need to rename the column with the video ID to match up with that in the vids_df
#    cols = list(results_info_df.columns)
#    cols[-2] = 'VidID'
#    results_info_df.columns = cols
#    results_info_df = results_info_df.merge(
#        right=vids_df,
#        how='left',
#        on='VidID',
#        suffixes=('_comm', '_vid'))
    
    # Remove duplicated comments:
#    results_info_df.drop_duplicates(subset='CommID', inplace=True)
    
    #### Lastly get the channel info:
    
    # Rename common columns:
#    cols = list(results_info_df.columns)    
#    cols[5] = 'publishedAt_comm'    
#    results_info_df.columns = cols    
#    results_info_df = results_info_df.merge(
#        right=chan_info_df,
#        how='left',
#        on='ChannelID',
#        suffixes=('_vid', '_chan'))
    
    
    ###########################################################################
    
    # Remove duplicated comments:
    results_info_df.drop_duplicates(subset='CommID', inplace=True)
    
    # Number of comments and channels to display (atm hard coded at 6)
    num_disp = 6
    
    # Create list with the comment data to send back:
    comm_dict_list = create_comm_list(results_info_df, 
                                      num_disp)
    
    
    # Create a listing of the channels associated with the comments, 
    # in order of sum of the sim_score
    
    sim_sum_dict = {}

    for chanID in set(results_info_df['ChannelID']):
        try:
            sim_sum_dict[chanID] = sum(results_info_df[results_info_df['ChannelID'] == chanID]['sim_score'])
        except:
            print('There was an error in processing the sum of the similarity score')
    
    sim_sum_sorted_dict = {key: val for key, val 
                           in 
                           sorted(sim_sum_dict.items(), 
                                  reverse=True, 
                                  key=lambda item: item[1])}
    
    # Create list with the channel data to send back:
    
    chan_dict_list = create_chan_list(sim_sum_sorted_dict, 
        results_info_df, 
        num_disp)

    return chan_dict_list, comm_dict_list




# Add new column to comments table (only do once - sim_score)

# Update the column and assign the similarity scores for the given search

# Pick out top whatever number of comments (order by sim_score) to save as dataframe

# SQL query the relevant video and channel information as well




































