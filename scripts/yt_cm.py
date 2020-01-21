## Script used to download all comments given a video ID into a pandas df and
## then save as a .csv file

# Input: videoID
# Output: dataframe of comments

import os
import time
import googleapiclient.discovery
import pandas as pd


with open(os.getcwd()[0:19]+'\\Documents\\GitHub\\YT_API_key.txt','r') as f_API:
    DEVELOPER_KEY = f_API.read()

# Get one page of comments
def get_comments_page(vid_ID, order_option,pagetok=None):
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)

    request = youtube.commentThreads().list(
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
def create_comments_df(vid_ID, order_option='relevance', max_pgs=10):
    
    thread_list = []

    currentcomments = get_comments_page(vid_ID,order_option)
    thread_list = thread_list + currentcomments["items"]
    priorcomments = currentcomments   
    
    for i in range(0,max_pgs):
        try:
            currentcomments = get_comments_page(vid_ID,order_option,priorcomments['nextPageToken'])
            thread_list = thread_list + currentcomments["items"]
            priorcomments = currentcomments
        except KeyError:
            break
            
    
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






