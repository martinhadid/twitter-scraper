import datetime
import config
from twitterclient import TwitterClient


class Tweet:
    def __init__(self, tweet_id=None, date=None, username=None, text=None, hashtags=None, replies=None, retweets=None,
                 likes=None):
        self.tweet_id = tweet_id
        self.date = date
        self.username = username
        self.text = text
        self.hashtags = hashtags
        self.replies = replies
        self.retweets = retweets
        self.likes = likes
        self._val = True
        self._sentiment = None

    def __bool__(self):
        return self._val

    def __eq__(self, other):
        if self.tweet_id == other.tweet_id:
            return True
        else:
            return False

    def _fetch_tweet_id(self, scrap):
        """Sets tweet id from scrap"""
        self.tweet_id = str(scrap.find('a', class_='tweet-timestamp js-permalink js-nav js-tooltip').attrs.get(
            'data-conversation-id'))

    def _fetch_date(self, scrap, datetime_format=False):
        """Sets tweet date from scrap"""
        date = scrap.find('span', class_='_timestamp').attrs.get('data-time')
        if datetime_format:
            self.date = str(datetime.datetime.fromtimestamp(int(date)))
        else:
            self.date = str(date)

    def _fetch_username(self, scrap):
        """Sets username from scrap"""
        self.username = '@' + scrap.find('span', class_='username').find('b').string

    def _fetch_text(self, scrap):
        """Sets tweet text from scrap"""
        tweets = scrap.find('p', class_='tweet-text').strings
        tweet_text = ''.join(tweets)
        tweet_text = tweet_text.replace('\n', ' ')
        self.text = tweet_text

    def _fetch_hashtags(self, scrap):
        """Sets hashtags from scrap"""
        hashtags_list = [''.join(hashtag.strings) for hashtag in scrap.find_all('a', class_='twitter-hashtag')]
        self.hashtags = hashtags_list

    def _fetch_counters(self, scrap):
        """Sets all counters (retweets, likes and replies) from scrap"""
        tweet_counters = scrap.find_all('span', class_='ProfileTweet-actionCountForAria')
        self.retweets = tweet_counters[config.tweet['retweets']].string.split(' ')[0]
        self.likes = tweet_counters[config.tweet['likes']].string.split(' ')[0]
        self.replies = tweet_counters[config.tweet['replies']].string.split(' ')[0]

    def _remove_punctuations(self):
        self.retweets = int(self.retweets.replace(',', '').replace('.', ''))
        self.likes = int(self.likes.replace(',', '').replace('.', ''))
        self.replies = int(self.replies.replace(',', '').replace('.', ''))

    def enrich_tweet(self, scrap):
        """Function that calls all tweet fetchers """
        self._fetch_counters(scrap)
        self._remove_punctuations()
        self._fetch_text(scrap)
        self._fetch_hashtags(scrap)
        self._fetch_date(scrap, False)
        self._fetch_username(scrap)
        self._fetch_tweet_id(scrap)
        self._sentiment = TwitterClient().get_sentiment(self.text)

    def false_tweet(self):
        """Sets tweet object to false object"""
        self._val = False

    def set_internal_id(self, internal_id):
        """Sets internal id of tweet when gathered by db."""
        self.internal_id = internal_id
