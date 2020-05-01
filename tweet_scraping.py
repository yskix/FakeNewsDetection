#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 12:38:33 2020

@author: rabeet
"""

from twython import Twython
import pickle, os
from time import sleep

def read_data_from_pickle(infile):
    with open (infile, 'rb') as fp:
        return pickle.load(fp)
    
def save_data_to_pickle(outfile, all_tweets):
    with open(outfile, 'wb') as fp:
        pickle.dump(all_tweets, fp)

# API Keys
ConsumerKey = 'gQds0Z5uYhf3uBkLDWTXxwJyR'
ConsumerSecret = 'Vw1BEAfoqqcZxlGW1VeV4eTowrohXhVMagUYKSJn2dfyz1vOB7'
AccessToken = '1476579756-zgvKwQ40zh2Nxi8nPEvZyEN5Coo6YGcy3qDSK4q'
AccessSecret = 'MaodbtGGpN0YEgOwIBqf6vf5pL5R34QDOAs3iyfzT1mPo'

# Initialize Tweet scraper and Vader analyzer
twitter = Twython(ConsumerKey, ConsumerSecret, AccessToken, AccessSecret)

existing_tweets = []
if os.path.isfile('./data/all_tweets'):
    existing_tweets = read_data_from_pickle('./data/all_tweets')

existing_tweets_ids = [tweet['id'] for tweet in existing_tweets]

# Create list of usernames for scraping
NAMES = ['WHO', 'YahooNews', 'googlenews', 'HuffPost' , 'CNN', 'nytimes', 'FoxNews', 'NBCNews',
          'MailOnline', 'washingtonpost', 'guardian', 'WSJ', 'ABC', 'BBCNews', 'USATODAY', 'latimes',
          'dawn_com', 'geonews_urdu', 'thenews_intl', 'etribune', 'dailytimespak', 'The_Nation',
          'ePakistanToday', 'SAMAATV', 'ARYNEWSOFFICIAL', 'ExpressNewsPK', 'PTVNewsOfficial',
          'BillGates', 'elonmusk', 'GretaThunberg', 'realDonaldTrump', 'ImranKhanPTI', 'narendramodi',
          'JustinTrudeau', 'BarackObama', 'GH_PARK', 'netanyahu', 'khamenei_ir', 'KingSalman',
          'dilmabr', 'AbeShinzo', 'fhollande', 'David_Cameron', 'Pontifex', 'Queen_Europe',
          'KremlinRussia_E', 'nhsrcofficial', 'NIH_Pakistan']

# NAMES = ['WHO']
for NAME in NAMES:
    user_timeline = twitter.get_user_timeline(screen_name=str(NAME) ,count=200, tweet_mode='extended')
    BREAK = False
    # user_timeline = twitter.get_user_timeline(screen_name=str(NAME) ,count=200, tweet_mode='extended', lang = 'en')
    while len(user_timeline) != 0 and BREAK == False:        
        for tweet in user_timeline:
            if tweet['id'] in existing_tweets_ids:
                print("Duplicate Tweet Found")
                BREAK = True
                break
            else:
                existing_tweets.append(tweet)

        if len(user_timeline) != 0 and BREAK == False:
            user_timeline = twitter.get_user_timeline(screen_name=str(NAME),
                                                      count=200,
                                                      tweet_mode='extended',
                                                      max_id=(user_timeline[len(user_timeline)-1]['id'])-1)
    sleep(5)

save_data_to_pickle('./data/all_tweets', existing_tweets)