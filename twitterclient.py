import tweepy
from tweepy import OAuthHandler
import config
from user import User
from logger import Logger
import re
from textblob import TextBlob

"""global variable to log info and error to scraper_logs"""
logger = Logger()


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
            users_with_data = []
            for user in users:
                user_data = self.api.get_user(id=user)
                users_with_data.append(User(user,
                                            user_data.followers_count,
                                            user_data.friends_count,
                                            user_data.statuses_count))
            return users_with_data

        except tweepy.TweepError as err:
            logger.error('Error : ' + str(err))

    def clean_tweet(self, tweet):
        ''' Function to clean tweet text'''
        return ' '.join(re.sub('(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) | (\w+:\ / \ / \S+)', ' ', tweet).split())

    def get_sentiment(self, tweet_text):
        ''' Function to classify sentiment of the tweet '''
        analysis = TextBlob(self.clean_tweet(tweet_text))
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'
