import tweepy
from tweepy import OAuthHandler
import config
import api_translator

class TwitterClient(object):
    '''Generic Twitter Class for sentiment analysis.'''

    def __init__(self):
        ''' Class constructor or initialization method.'''
        # keys and tokens from the Twitter Dev Console
        self._consumer_key = config.API['consumer_key']
        self._consumer_secret = config.API['consumer_secret']
        self._access_token = config.API['access_token']
        self._access_token_secret = config.API['access_token_secret']

        try:
            self.auth = OAuthHandler(self._consumer_key, self._consumer_secret)
            self.auth.set_access_token(self._access_token, self._access_token_secret)
            self.api = tweepy.API(self.auth)
        except Exception:
            print("Authentication Failed")

    def get_user(self, user):
        '''Main function to fetch tweets and parse them.'''
        tweets = []
        try:
            user = self.api.get_user(id=user)
            return user

        except tweepy.TweepError as e:
            print("Error : " + str(e))


def main():
    print
    api = TwitterClient()
    # tweets = api.get_tweets(query='Bitcoin', count=1)
    user = api.get_user('@fcbarcelona')
    user = api_translator.from_api_user(user)
    print('\n\n\n',user.total_tweets,user.username, user.following,user.followers)


if __name__ == '__main__':
    main()
