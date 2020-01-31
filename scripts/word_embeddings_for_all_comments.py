# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 22:38:28 2020

Code to run overnight to get all comments processed through spaCy

@author: Ronald Maj
"""

import pickle
import pandas as pd
import spacy
from tqdm import tqdm



insight_dir = 'C:\\Users\\Ronald Maj\\Documents\\GitHub\\InsightDataProject\\'

comms_df = pd.read_csv(insight_dir+'data\\cleaned\\all_comments_dup_na_clean_df.csv', index_col=0)
all_comm_docs = comms_df['textDisplay']



# Load language model
nlp = spacy.load("en_core_web_lg")



def clean_text(text):
    # lower case:
    text = text.lower()
    
    # replace new line and return with space
    text = text.replace("\n", " ").replace("\r"," ")
    
    # replace punctuation marks with space
    punc_list = '#/<>@[\]{}|^~'
    t=str.maketrans(dict.fromkeys(punc_list, ""))
    text = text.translate(t)
    return text

all_comm_docs = [clean_text(doc) for doc in all_comm_docs]



# Cleaning emojis
def deEmojify(inputString):
    return inputString.encode('ascii', 'ignore').decode('ascii')

all_comm_docs = [deEmojify(doc) for doc in all_comm_docs]



for i in range(0,650000,10000):
    
    spa_docs= []
    
    for doc in tqdm(all_comm_docs[i:i+10000]):
        # Passes that article through the pipeline and adds to a new list.
        pr = nlp(doc)
        spa_docs.append(pr)
    with open('D:\\Pickle_files-Embedded-YT-Comments\\comms_spa_'+str(i+1)+'.pkl', 'wb') as f:
        pickle.dump(spa_docs, f)
    
    if i == 640000:
        for doc in tqdm(all_comm_docs[i+10000:]):
            # Passes that article through the pipeline and adds to a new list.
            pr = nlp(doc)
            spa_docs.append(pr)
        with open('D:\\Pickle_files-Embedded-YT-Comments\\comms_spa_'+str(i+10000)+'.pkl', 'wb') as f:
            pickle.dump(spa_docs, f)
    
    first_idx = i
    last_idx = i+10000
    
    
