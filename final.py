#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  2 02:00:38 2020

@author: ix
"""

from fastai.text import *
import numpy as np
#%tensorflow_version 1.x
#import tensorflow as tf
from bert_serving.client import BertClient
from termcolor import colored
import pandas as pd
import json
from gensim import corpora, models
import pickle, re
import nltk
nltk.download()
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from nltk.util import ngrams
import pandas as pd
import argparse


def Sentiments (query):
    bs = 24
    seed = 333
    data_lm = load_data('.','data_clas.pkl')
    learn = text_classifier_learner(data_lm, AWD_LSTM, drop_mult=0.5)
    learn.load_encoder('fine_tuned_encoder')
    learn.load('final_class')
    return learn.predict(query)[0]


NUM_GRAMS = 2
additional_stop_words=['hrtechconf','peopleanalytics','hrtech','hr','hrconfes',
                       'hrtechnology','voiceofhr','hrtechadvisor','gen','wait',
                       'next','see','hcm','booth','tech','la','vega','last',
                       'look','technology','work', 'announce','product','new',
                       'team','use','happen','time','take','make','everyone',
                       'anyone','week','day','year','let','go','come','word',
                       'employee','get','people','today','session','need',
                       'meet','help','talk','join','start','awesome','great',
                       'achieve','job','tonight','everyday','room','ready',
                       'one','company','say','well','data','share','love',
                       'want','like','good','business','sure','miss','demo',
                       'live','min','play','always','would','way','almost',
                       'thank','still','many','much','info','wow','play','full',
                       'org','create','leave','back','front','first','may',
                       'tomorrow','yesterday','find','stay','add','conference',
                       'top','stop','expo','hall','detail','row','award','hey',
                       'continue','put','part','whole','some','any','everywhere',
                       'convention','center','forget','congratulation','every',
                       'agenda','gift','card','available','behind','meeting',
                       'best','happen','unlockpotentialpic','half','none',
                       'human', 'resources','truly','win','possible','thanks',
                       'know','check','visit','fun','give','think','forward',
                       'twitter','com','pic','rt','via']

def read_data_from_pickle(infile):
    with open (infile, 'rb') as fp:
        return pickle.load(fp)

def get_wordnet_pos(word):
    """
    Map POS tag to first character lemmatize() accepts
    """
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}

    return tag_dict.get(tag, wordnet.NOUN)

def text_cleanup(text):  
    '''
    Text pre-processing
        return tokenized list of cleaned words
    '''
    # Convert to lowercase
    text = str(text)
    text_clean = text.lower()
    # Remove non-alphabet
    text_clean = re.sub(r'[^a-zA-Z]|(\w+:\/\/\S+)',' ', text_clean).split()    
    # Remove short words (length < 3)
    text_clean = [w for w in text_clean if len(w)>2]
    # Lemmatize text with the appropriate POS tag
    lemmatizer = WordNetLemmatizer()
    text_clean = [lemmatizer.lemmatize(w, get_wordnet_pos(w)) for w in text_clean]
    # Filter out stop words in English 
    stops = set(stopwords.words('english')).union(additional_stop_words)
    text_clean = [w for w in text_clean if w not in stops]
    
    return text_clean

def word_grams(words, min=1, max=2):
    '''
    Build ngrams word list
    '''
    word_list = []
    for n in range(min, max):
        for ngram in ngrams(words, n):
            word_list.append(' '.join(str(i) for i in ngram))
    return word_list

def inference(article):
    tokenized = text_cleanup(article)
    ngram = word_grams(tokenized, NUM_GRAMS, NUM_GRAMS+1)
    corpus_test = tweets_dict.doc2bow(ngram)
    result = lda_model.get_document_topics(corpus_test)
    topic_names = [lda_model.show_topic(x[0], 1)[0][0] for x in result]
    sorted_result = sorted(result, key = lambda x:x[1], reverse=True)
    return sorted_result, topic_names

lda_model = models.ldamodel.LdaModel.load('./models/tweets_lda.model')
cleaned_tweets_ngram = read_data_from_pickle('./models/cleaned_tweets_ngrams')
tweets_dict = corpora.Dictionary(cleaned_tweets_ngram)
tweets_dict.filter_extremes(no_below=10, no_above=0.5)


def testing(query,jsonpath):
        
        
    # Reading the json as a dict
    with open(jsonpath) as json_data:
        data = json.load(json_data)
    
	# using the from_dict load function. Note that the 'orient' parameter 
	#is not using the default value (or it will give the same error than you had)
	# We transpose the resulting df and set index column as its index to get this result
    sources = list(data.keys())
    values = list(data.values())
    final_values = []
    string = "WHO guidance helps detect iron deficiency and protect brain development ITU-WHO Joint Statement: Unleashing information technology to defeat COVID-19 Joint statement by WTO Director-General Roberto Azevêdo and WHO Director-General Tedros Adhanom Ghebreyesus"
    for value in values:
        joined_val = [" ".join(value)]
        final_values.append(str(joined_val).replace(string,""))

    dataframe = pd.DataFrame(data=[sources,final_values]).T
    dataframe.columns = ["source","full_text"]
    
    Pairs = []
    for i in range(len(dataframe)):
        Pairs.append([str(query),dataframe.iloc[i]['full_text']])
    return Pairs,dataframe	

def scoring(pair):
    import math
    query_vec_1, query_vec_2 = bc.encode(pair)
    cosine = np.dot(query_vec_1, query_vec_2) / (np.linalg.norm(query_vec_1) * np.linalg.norm(query_vec_2))
    return 1/(1 + math.exp(-100*(cosine - 0.95)))

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-n", "--news", required=True,
	help="text of the news")
args = vars(ap.parse_args())

#query = "Covid19 is deadly and spreads through 5G" ## change or input query here
query = args["news"]

json_path = "who_scrap.json"   ## data corpus
indices = []
scores =[]

with BertClient(port=5555, port_out=5556, check_version=False) as bc:
    Pairs,dataframe = testing(query,json_path)
    print("Start testing")    
    for i, p in enumerate(Pairs):
        try:
            score = scoring(p)
            #print("Similarity of Pair {}: ".format(i+1),score )
            if score > 0.7:
                indices.append(i)
                scores.append(score)
        except:
            print("no text found for entry {}".format(i+1))
    result_df = dataframe.iloc[indices]
	
weight = 0
sentiments = 0 	
for i in range(len(result_df)):
	weight = weight+score[i]
	if Sentiments(query) == Sentiments(result_df.iloc[i]['full_text']):
		sentiments = sentiments+1
weight = weight/len(result_df)
sentiments = sentiments/len(result_df)
classify = weight*0.70 + 0.2(sentiments)
if classify >0.8:
    print('True')
else:
    print ('Fake')
	
