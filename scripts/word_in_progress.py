# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 21:59:18 2020

Script used for cleaning / processing text

@author: Ronald Maj
"""



#### Load function to go here:
comms_df = pd.read_csv(insight_dir+'data\\processed\\all_comments_dup_na_clean_df.csv', index_col=0)


comms_samp_df = comms_df.sample(50000)

len(comms_samp_df)

# Get just the comment text from the dataframe:

comms_samp_df['textDisplay']

comms_samp_df[comms_samp_df.duplicated()]

##### Create a list to put into spaCy, clean the comments then run through the spaCy pipeline:

comm_docs = comms_samp_df['textDisplay']

def clean_text(text):
    # lower case:
    text = text.lower()
    
    # replace new line and return with space
    text = text.replace("\n", " ").replace("\r"," ")
    
    # replace punctuation marks with space
    punc_list = '#/<>@[\]{}|^~'
    t=str.maketrans(dict.fromkeys(punc_list, ""))
    
    return text

comm_docs = [clean_text(doc) for doc in comm_docs]

# Cleaning emojis
def deEmojify(inputString):
    return inputString.encode('ascii', 'ignore').decode('ascii')

comm_docs = [deEmojify(doc) for doc in comm_docs]

nlp2 = spacy.load("en_core_web_lg")

spa_docs= []
for doc in tqdm(comm_docs):
    # Passes that article through the pipeline and adds to a new list.
    pr = nlp2(doc)
    spa_docs.append(pr)
    
    
### Create a matrix of the database:

# Empty matrix
comms_vec = np.zeros((len(spa_docs),300))

# Go through each doc and save the word2vec vector to the matrix:
for idx,doc in enumerate(spa_docs):
    comms_vec[idx] = doc.vector.reshape(1,-1)