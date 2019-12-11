import tweepy
from tweepy import OAuthHandler
import config
from user import User
import logger
import re
from textblob import TextBlob
from databasemanager import DatabaseManager
from mysql import connector

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
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) | (\w+:\ / \ / \S+)", " ", tweet).split())

    def get_tweet_sentiment(self, tweet):
        ''' Function to classify sentiment of the tweet '''
        analysis = TextBlob(self.clean_tweet(tweet))
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'

    def get_tweets_text_sentiment(self):
        '''Function to pun'''
        with DatabaseManager(config.database_name) as db:
            db.use_db()
            tweets = db.run_query('''SELECT TWEET_ID, TWEET_TEXT FROM TWEET WHERE SENTIMENT IS NULL''')

        parsed_tweet = [{'ID': tweet[0], 'sentiment': self.get_tweet_sentiment(tweet[1])} for tweet in tweets]
        return parsed_tweet


def main():
    api = TwitterClient()
    sentiments = api.get_tweets_text_sentiment()
    positive_tweets = [1 for sentiment in sentiments if sentiment['sentiment'] == 'positive']
    negative_tweets = [-1 for sentiment in sentiments if sentiment['sentiment'] == 'negative']
    neutral_tweets = [0 for sentiment in sentiments if sentiment['sentiment'] == 'neutral']






'''    
    # picking positive tweets from tweets
    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
    # percentage of positive tweets
    print("Positive tweets percentage: {} %".format(100 * len(ptweets) / len(tweets)))
    # picking negative tweets from tweets
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
    # percentage of negative tweets
    print("Negative tweets percentage: {} %".format(100 * len(ntweets) / len(tweets)))
    # percentage of neutral tweets
    print("Neutral tweets percentage: {} %".format(100 * len(tweets - ntweets - ptweets) / len(tweets)))

    # printing first 5 positive tweets
    print("\n\nPositive tweets:")
    for tweet in ptweets[:10]:
        print(tweet['text'])

    # printing first 5 negative tweets
    print("\n\nNegative tweets:")
    for tweet in ntweets[:10]:
        print(tweet['text'])
'''

if __name__ == "__main__":
    main()
