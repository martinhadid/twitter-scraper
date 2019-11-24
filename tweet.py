import datetime

COUNTER_INDEX = {'replies': 0, 'retweets': 1, 'likes': 2}


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

    def _fetch_tweet_id(self, scrap):
        self.tweet_id = str(scrap.find('a', class_='tweet-timestamp js-permalink js-nav js-tooltip').attrs.get(
            'data-conversation-id'))

    def _fetch_date(self, scrap, datetime_format=False):
        date = scrap.find('span', class_='_timestamp').attrs.get('data-time')
        if datetime_format:
            self.date = str(datetime.datetime.fromtimestamp(int(date)))
        else:
            self.date = str(date)

    def _fetch_username(self, scrap):
        self.username = '@' + scrap.find('span', class_='username').find('b').string

    def _fetch_text(self, scrap):
        tweets = scrap.find('p', class_='tweet-text').strings
        tweet_text = ''.join(tweets)
        tweet_text = tweet_text.replace('\n', ' ')
        self.text = tweet_text

    def _fetch_hashtags(self, scrap):
        hashtags_list = [''.join(hashtag.strings) for hashtag in scrap.find_all('a', class_='twitter-hashtag')]
        hashtags_text = ' '.join(hashtags_list)
        self.hashtags = hashtags_text

    def _fetch_counters(self, scrap):
        tweet_counters = scrap.find_all('span', class_='ProfileTweet-actionCountForAria')
        self.retweets = tweet_counters[COUNTER_INDEX['retweets']].string.split(' ')[0]
        self.likes = tweet_counters[COUNTER_INDEX['likes']].string.split(' ')[0]
        self.replies = tweet_counters[COUNTER_INDEX['replies']].string.split(' ')[0]

    def enrich_tweet(self, scrap):
        self._fetch_counters(scrap)
        self._fetch_text(scrap)
        self._fetch_hashtags(scrap)
        self._fetch_date(scrap, True)
        self._fetch_username(scrap)
        self._fetch_tweet_id(scrap)
