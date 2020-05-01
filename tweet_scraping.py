from twython import Twython
import pickle, os
from time import sleep
from LDA_Inference import inference

def read_data_from_pickle(infile):
    with open (infile, 'rb') as fp:
        return pickle.load(fp)
    
def save_data_to_pickle(outfile, all_tweets):
    with open(outfile, 'wb') as fp:
        pickle.dump(all_tweets, fp)

# API Keys
keys = read_data_from_pickle('./data/api_keys')
ConsumerKey = keys[0]
ConsumerSecret = keys[1]
AccessToken = keys[2]
AccessSecret = keys[3]

# Initialize Tweet scraper
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
                full_text = tweet['full_text']
                tweet_topic, topic_names = inference(full_text)
                tweet['topic'] = [tweet_topic[0:3] if len(tweet_topic) != 30 else 'None']
                existing_tweets.append(tweet)

        if len(user_timeline) != 0 and BREAK == False:
            user_timeline = twitter.get_user_timeline(screen_name=str(NAME),
                                                      count=200,
                                                      tweet_mode='extended',
                                                      max_id=(user_timeline[len(user_timeline)-1]['id'])-1)
    sleep(5)

save_data_to_pickle('./data/all_tweets', existing_tweets)