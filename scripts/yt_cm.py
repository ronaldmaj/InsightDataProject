## Script used to download all comments given a video ID into a pandas df and
## then save as a .csv file

# Input: videoID
# Output: dataframe of comments

import os
import time
import googleapiclient.discovery
import googleapiclient.errors
import pandas as pd


with open(os.getcwd()[0:19]+'\\Documents\\GitHub\\YT_API_key.txt','r') as f_API:
    DEVELOPER_KEY = f_API.read()

def set_up_YT_client():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"

    return googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)

# Get one page of comments
def get_comments_page(YT_client,vid_ID, order_option,pagetok=None):
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.

    request = YT_client.commentThreads().list(
        part="snippet,replies",
        maxResults=100,
        order=order_option,
        pageToken = pagetok,
        textFormat="plainText",
        videoId=vid_ID
    )
    response = request.execute()
    time.sleep(0.3)
    return response



# Given a YouTube videoID, the following function creates a list of 
# comment threads (including replies). Also 
def create_comments_df(YT_client, vid_ID, order_option='relevance', max_pgs=1):
    # Get initial comments
    thread_list = []
    currentcomments = get_comments_page(YT_client,vid_ID,order_option)
    thread_list = thread_list + currentcomments["items"]
    priorcomments = currentcomments
    
    # Run through the number of pages requested and build up comment corpus
    for i in range(0,max_pgs):
        try:
            currentcomments = get_comments_page(YT_client,vid_ID,order_option,priorcomments['nextPageToken'])
            thread_list = thread_list + currentcomments["items"]
            priorcomments = currentcomments
        except KeyError:
            break
    
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
    
    return df_comms

# Given a YouTube channel link, download the comments from the n most recent 
# videos from that channel.
    
#def get_channel_from_category(YT_client, categoryID):

#    request = YT_client.channels.list(
#        part="contentDetails",
#        maxResults=100,
#        order=order_option,
#        pageToken = pagetok,
#        textFormat="plainText",
#        videoId=vid_ID
#    )
#    response = request.execute()

def get_channel_IDs(YT_client,cat_num):

    request = YT_client.channels.list(
        part="snippet",
        categoryId=cat_num
    )
    response = request.execute()
    return response

def get_videos_of_channel(YT_client, channelID):
    request = YT_client.playlistItems().list(
        part="snippet",
        maxResults=50,
        playlistId = 'UU'+channelID[2:]
    )
    response = request.execute()
    time.sleep(0.3)
    return response

# -*- coding: utf-8 -*-

# Sample Python code for youtube.search.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python


scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]



def search_results(YT_client,query):

    request = YT_client.search().list(
        part="snippet",
        maxResults=50,
        publishedBefore="2020-01-01T00:00:00Z",
        q=query,
        type="channel",
        order='relevance',
        relevanceLanguage ='en'
    )
    response = request.execute()
    time.sleep(0.3)
    return response

# -*- coding: utf-8 -*-

# Sample Python code for youtube.guideCategories.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python


scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

def main2():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"

    # Get credentials and create an API client
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)

    # List the guide categories from YouTube for Canada
    request = youtube.guideCategories().list(
        part="snippet",
        regionCode="CA"
    )
    response = request.execute()
    time.sleep(0.3)
    return response




