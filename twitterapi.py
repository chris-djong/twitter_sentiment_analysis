import tweepy
import pandas as pd
import numpy as np 
import datetime
import re # regular expression module 
from database_connection import DatabaseConnection
import flair 

from textblob import TextBlob
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer


class TwitterApi():
    def __init__(self):
        # Obtain all of the required api keys
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
    def get_tweets_by_keyword(self, keyword, date, n_tweets=1000):
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
        polarities = []
        for text in self.tweets:
            sentence = flair.data.Sentence(text)
            sentiment_model.predict(sentence)

            if sentence.labels[0].value == 'NEGATIVE':
                score = -sentence.labels[0].score
            else:
                score = sentence.labels[0].score
            polarities.append(score)
            
            if (score < -0.33):
                self.negative_tweets += 1
            elif score < 0.33:
                self.neutral_tweets += 1
            else:
                self.positive_tweets += 1
        
        self.polarity = np.average(polarities)

             

    # This function creates a connection to the postgres database and obtains all the stocks 
    def download_twitter_data_today(self):
        # First create a connection to the database and execute the query to obtain all the stocks
        connection = DatabaseConnection()
        today = datetime.date.today()
        stocks = connection.execute_select_query('SELECT * FROM stocks_stock;')
        # Loop through all the stocks and get the corresponding tweets
        for stock in stocks:
            # Make the API search for all tick containing either the ticker or the full name [here we should remove Inc, Corp etc]
            ticker = stock['ticker'].split('-')[0]
            ticker = ticker.split('.')[0]
            keyword = '(' + stock.name + ' OR ' + ticker +  ') (lang:en)'

            # Get the tweets and analyse them 
            get_tweets_by_keyword(ticker, today)
            analyse_tweets()
            
            # And finally send the result back to the database
            connection.execute_insert_query('INSERT INTO twitterapi.TweetHistory (Stock, date, n_positive, n_negative, n_neutral, polarity) VALUES (%s, %s, %s, %s, %s, %s)' % (stock['id'], today, self.positive_tweets, self.negative_tweets, self.neutral_tweets, self.polarity))
            print('Succesfully inserted %s into database' % (stock))

       

        

            
        



