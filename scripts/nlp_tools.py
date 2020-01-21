# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 14:52:30 2020

Written based on the work of:
https://towardsdatascience.com/benchmarking-python-nlp-tokenizers-3ac4735100c5

@author: Ronald Maj
"""

from nltk.tokenize.regexp import regexp_tokenize


def clean_text(text):
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

def renltk_tokenize(text):
    text= clean_text(text)
    # search for any white space and tokenize as word using regex '\s+' 
    words = regexp_tokenize(text, pattern = '\s+', gaps=True)
    return words

