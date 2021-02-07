 
from .twitterapi import TwitterApi 
from core.celery import app
from .models import TweetHistory
from ..stocks.models import Stock
import datetime
import time
from tqdm import tqdm

 # Task that downloads the weekly google data for each user today
@app.task
def download_user_twitter_data_today():
    return None

# Task that download the weekly google data for each stock today
@app.task
def download_all_twitter_data_today():
    today = datetime.date.today()
    stocks = Stock.objects.all()

    # Create the api object
    twitter_api = TwitterApi()
    for stock in stocks:
        # Get and analyse the tweets
        ticker = stock.ticker.split('-')[0]
        ticker = ticker.split('.')[0]

        keyword = stock.name + ' OR ' + ticker

        # Get and analyse the tweets
        twitter_api.get_tweets_by_keyword(keyword=keyword, date=today)
        twitter_api.analyse_tweets()

        # Delete all previous objects 
        previous_tweet_analysis = TweetHistory.objects.filter(stock=stock, date=today)
        previous_tweet_analysis.delete()

        # And create a new objects
        TweetHistory.objects.create(stock=stock, date=today, n_tweets=twitter_api.n_tweets, n_negative=twitter_api.negative_tweets, n_positive=twitter_api.positive_tweets, n_neutral=twitter_api.neutral_tweets, overal_polarity=twitter_api.polarity)
        


# Task that download the weekly google data for each stock for a given date
@app.task
def download_all_twitter_data_date(date):
    stocks = Stock.objects.all()

    # Create the api object
    twitter_api = TwitterApi()
    for stock in tqdm(stocks):
        # Get and analyse the tweets
        ticker = stock.ticker.split('-')[0]
        ticker = stock.ticker.split('.')[0]

        keyword = stock.name + ' OR ' + ticker

        twitter_api.get_tweets_by_keyword(keyword=keyword, date=date)
        twitter_api.analyse_tweets()

        # Delete all previous objects 
        previous_tweet_analysis = TweetHistory.objects.filter(stock=stock, date=date)
        previous_tweet_analysis.delete()

        # And create a new objects
        TweetHistory.objects.create(stock=stock, date=date, n_tweets=twitter_api.n_tweets, n_negative=twitter_api.negative_tweets, n_positive=twitter_api.positive_tweets, n_neutral=twitter_api.neutral_tweets, overal_polarity=twitter_api.polarity)
        

