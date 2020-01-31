# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 10:30:39 2020

Script for creating and saving the word2vec matrix for each comment

@author: Ronald Maj
"""
import os
import pickle
import numpy as np
import pandas as pd

import spacy
from tqdm import tqdm

# Load language model
nlp = spacy.load("en_core_web_lg")

# Main Directory:
insight_dir = 'C:\\Users\\Ronald Maj\\Documents\\GitHub\\InsightDataProject\\'

# Load comment csv file:
comms_df = pd.read_csv(insight_dir+'data\\cleaned\\all_comments_dup_na_clean_df.csv', index_col=0)

all_comm_docs = comms_df['textDisplay']

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


# Load list of pickle files:
pickle_files = os.listdir('D:\\Pickle_files_Embedded_YT_Comments\\')

# Empty matrix
comms_mat = np.zeros((len(comms_df),300))

for file in pickle_files:
    
    with open('D:\\Pickle_files_Embedded_YT_Comments\\'+file, 'rb') as f:
        docs_10k = pickle.load(f)
        
        strt = int(file[-10:-4])-1
        end = strt + len(docs_10k)
        
        for i in tqdm(range(strt,end)):
            comm_vec = docs_10k[i-strt].vector.reshape(1,-1)
            comms_mat[i] = comm_vec
            
np.savetxt('D:\\Pickle_files_Embedded_YT_Comments\\comms_mat.txt',comms_mat)
np.savetxt('D:\\Pickle_files_Embedded_YT_Comments\\comms_mat.csv',comms_mat)

np.save('D:\\Pickle_files_Embedded_YT_Comments\\comms_mat.npy',comms_mat)

#%%
spa_docs= []

for doc in tqdm(all_comm_docs[640000:]):
    # Passes that article through the pipeline and adds to a new list.
    pr = nlp(doc)
    spa_docs.append(pr)

with open('D:\\Pickle_files_Embedded_YT_Comments\\comms_spa_6400001_end.pkl', 'wb') as f:
    pickle.dump(spa_docs, f)
    
for i in tqdm(range(0,len(spa_docs))):
    comm_vec = spa_docs[i].vector.reshape(1,-1)
    comms_mat[i+640000] = comm_vec

np.save('D:\\Pickle_files_Embedded_YT_Comments\\comms_mat_all.npy',comms_mat)
np.savetxt('D:\\Pickle_files_Embedded_YT_Comments\\comms_mat_all.txt',comms_mat)
np.savetxt('D:\\Pickle_files_Embedded_YT_Comments\\comms_mat_all.csv',comms_mat)

