import tweepy
from textblob import TextBlob
import pandas as pd
import numpy as np 
import datetime
import re # regular expression module 
from .models import TwitterApiKey

import nltk
nltk.download('vader_lexicon')

from nltk.sentiment.vader import SentimentIntensityAnalyzer


class TwitterApi():
    def __init__(self):
        # Obtain all of the required api keys
        api_object = TwitterApiKey.objects.all()[0]
        self.ApiKey = api_object.key
        self.ApiSecret = api_object.key_secret
        self.ApiAccessToken = api_object.access_token
        self.ApiAccessTokenSecret = api_object.access_token_secret

        # And authenticate the class
        auth = tweepy.OAuthHandler(self.ApiKey, self.ApiSecret)
        auth.set_access_token(self.ApiAccessToken, self.ApiAccessTokenSecret)
        self.api = tweepy.API(auth, wait_on_rate_limit=True)

    # This function preprocesses a single tweet text
    def pre_process_tweet(self, text):
        # First remove retweet references / everything with 'RT @somewords: '
        text = re.sub(r'RT @\w+: ', '', text)
        # Remove (@word references) or (a number, A-Z, a-z followed by a tab character) or (a link) 
        text = re.sub(r'(@[A-Za-z0–9]+)|([0-9A-Za-z \t])|(\w+:\/\/\S+)', ' ', text)
        # Set to lowercase
        text = text.lower()
        return text

    # This function downloads all the tweets for a given keyword and saves them under self.tweets
    # By default a limit of 1000 tweets is imposed on the api to make sure that we are not blocked
    def get_tweets_by_keyword(self, keyword, date=datetime.date.today(), n_tweets=1000):
        until_date = date + datetime.timedelta(1)
        since_date = date - datetime.timedelta(1)
        tweets = tweepy.Cursor(self.api.search, q=keyword, since=since_date, until=until_date).items(n_tweets)
        self.tweets = np.array([])
        i = 0  # can be removed after initial testing
        for tweet in tweets:
            i+=1  # this can be removed after initial testing 
            text = self.pre_process_tweet(tweet.text)
            if text not in self.tweets:
                self.tweets = np.append(self.tweets, text)

        # These conditions can be removed after testing 
        if i == n_tweets:
            print('Maximum number of tweets has been detected for %s' % (keyword))
        elif i == 0:
            print('No tweets have been obtained for %s' % (keyword))

    def analyse_tweets(self):
        self.negative_tweets = 0
        self.positive_tweets = 0
        self.neutral_tweets = 0
        self.polarity = 0
        self.n_tweets = len(self.tweets)
        for text in self.tweets:
            # Polarity is a float that lies between [-1,1], -1 indicates negative sentiment and +1 indicates positive sentiments.
            analysis = TextBlob(text)
            self.polarity += analysis.sentiment.polarity
            
            # Valence aware dictionary for sentiment reasoning (VADER)
            score = SentimentIntensityAnalyzer().polarity_scores(text)
            # Find out whether this is a positive or negative tweet
            if score['neg'] > score['pos']:
                self.negative_tweets += 1
            elif score['pos'] < score['neg']:
                self.positive_tweets += 1
            else:
                self.neutral_tweets += 1

        

            
        



