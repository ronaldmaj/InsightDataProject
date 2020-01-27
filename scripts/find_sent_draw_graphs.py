# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 22:42:27 2020

Script to determine the engagement metrics and reaction of audience members

@author: Ronald Maj
"""
import os
import pandas as pd
from textblob import TextBlob
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
import re

insight_dir = os.getcwd()[0:19]+'\\Documents\\GitHub\\InsightDataProject\\'

comms_df = pd.read_csv(insight_dir+'data\\processed\\comments_df.csv', index_col=0)
vids_df = pd.read_csv(insight_dir+'data\\processed\\videos_top30_df.csv', index_col=0)
channels_df = pd.read_csv(insight_dir+'data\\processed\\channels_top50_df.csv', index_col=0)

test_cid = channels_df.iloc[1]['ChannelID']
test_vids_list = list(vids_df[vids_df['ChannelID'] == test_cid]['VidID'])

# Get just the comments from the test case
test_df = comms_df[comms_df['videoId'].isin(test_vids_list)]
test_commtext = test_df['textDisplay']


# Convert to list
data = test_commtext.values.tolist()

# Remove Emails
data = [re.sub('\S*@\S*\s?', '', sent) for sent in data]

# Remove new line characters
data = [re.sub('\s+', ' ', sent) for sent in data]

# Remove distracting single quotes
data = [re.sub("\'", "", sent) for sent in data]

def deEmojify(inputString):
    return inputString.encode('ascii', 'ignore').decode('ascii')

data = [deEmojify(comm) for comm in data]

def clean_text(text):
    # lower case:
    text = text.lower()
    # replace new line and return with space
    text = text.replace("\n", " ").replace("\r"," ")
    # replace punctuation marks with space
    punc_list = '!"#$%&()*+,-./:;<=>?@[\]{}|^_~' + '0123456789'
    t=str.maketrans(dict.fromkeys(punc_list, " "))
    text = text.translate(t)
    # replace single quote with empty character
    t = str.maketrans(dict.fromkeys("'`",""))
    
    text = text.translate(t)
    return text

blobs = []
for item in data:
    blobs.append(TextBlob(item))

sents = np.array([blob.sentiment.polarity for blob in blobs])

# Remove all neutral sentiments as they do not contribute much to gauging overall sentiment
sents_rm_neu_cassie = [x for x in sents if x != 0]

plt.figure(figsize=(8, 8))
plt.title('Sentiment Analysis - CaseyNeistat')
plt.xlabel('Polarity')
plt.ylabel('No. Comments')
sns.set_style('darkgrid')
sns.distplot(sents_rm_neu_cassie,kde=True)


test_df['Sentiment_Polarity'] = sents

vid_ids = list(set(test_df['videoId']))
sent_vids = []
for vid_ID in vid_ids:
    sent_vids.append(np.array(test_df[test_df['videoId'] == vid_ID]['Sentiment_Polarity']))

sent_vids_mean = [np.mean(sent_vids[i]) for i in range(0,len(sent_vids))]
sents_df = pd.DataFrame({'VidID':vid_ids, 'mean_sent':sent_vids_mean})
vids_df = pd.read_csv(insight_dir+'data\\processed\\videos_top30_df.csv', index_col=0)

import dateparser
published = []
for vid_id in sents_df['VidID']:
    published.append(dateparser.parse(vids_df[vids_df['VidID'] == vid_id]['VidPublished'].values[0]))

sents_df['Published'] = published

sents_df = sents_df.sort_values(by='Published')

vids_df['comm_views'] = vids_df['commentCount']/vids_df['viewCount']
vids_df['like_views'] = vids_df['likeCount']/vids_df['viewCount']
vids_df['dislike_views'] = vids_df['dislikeCount']/vids_df['viewCount']
vids_df['inter_views'] = (vids_df['likeCount']+vids_df['dislikeCount']+vids_df['commentCount'])/vids_df['viewCount']


sents_df.plot.line(x='Published',y='mean_sent',figsize=(15,8), marker='o',title='CaseyNeistat Mean Sentiment')
