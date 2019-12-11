import tweepy
from tweepy import OAuthHandler
import config
from user import User
import logger
from textblob import TextBlob
import re

"""global variable to log info and error to scraper_logs"""
logger = logger.Logger()


class TwitterClient:

    def __init__(self):
        '''API connector'''
        self._consumer_key = config.API['consumer_key']
        self._consumer_secret = config.API['consumer_secret']
        self._access_token = config.API['access_token']
        self._access_token_secret = config.API['access_token_secret']

        try:
            '''API Authentication'''
            self.auth = OAuthHandler(self._consumer_key, self._consumer_secret)
            self.auth.set_access_token(self._access_token, self._access_token_secret)
            self.api = tweepy.API(self.auth)
        except Exception:
            logger.error('Authentication Failed')

    def get_users_missing_data(self, users):
        '''Main function to fetch users and complete missing data.'''
        try:
            for user in users:
                user_data = self.api.get_user(id=user.username)
                return [User(user.username,
                             user_data.followers_count,
                             user_data.friends_count,
                             user_data.statuses_count)]

        except tweepy.TweepError as err:
            logger.error('Error : ' + str(err))

    def clean_tweet(self, tweet):
        ''' Utility function to clean tweet text'''
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) | (\w+:\ / \ / \S+)", " ", tweet).split())

    def get_tweet_sentiment(self, tweet):
        '''Classify sentiment of tweet'''
        analysis = TextBlob(self.clean_tweet(tweet))

        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'


