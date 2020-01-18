## Script used to figure out best way to 

# Input: videoID
# Output: dataframe of comments

with open(os.getcwd()[0:19]+'\\Documents\\GitHub\\YT_API_key.txt','r') as f_API:
    DEVELOPER_KEY = f_API.read()

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
    time.sleep(0.5)
    return response

# Given a YouTube videoID, the following function creates a data frame of comments (including replies)
def create_comments_df(vid_ID, order_option):
    nxt_pg_flag = 1
    items_list = []

    currentcomments = get_comments_page(vid_ID,order_option)
    items_list = items_list + currentcomments["items"]
    priorcomments = currentcomments

    while nxt_pg_flag == 1:
        try:
            currentcomments = get_comments_page(vid_ID,order_option,priorcomments['nextPageToken'])
            items_list = items_list + currentcomments["items"]
            priorcomments = currentcomments
        except KeyError:
            nxt_pg_flag = 0

    for item in items_list:
        data = {"CommID": item['id'], 'parentId': 0}
        data.update(item['snippet']["topLevelComment"]['snippet'])
        df_comms = df_comms.append(data,ignore_index=True)
        if 'replies' in item.keys():
            for reply in item['replies']['comments']:
                data = {"CommID": reply['id']}
                data.update(reply['snippet'])
                df_comms = df_comms.append(data,ignore_index=True)
    return df_comms