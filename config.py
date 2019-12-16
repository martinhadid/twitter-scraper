test_mode = True

scraper = {
    'csv_headers': ['tweet_id', 'date', 'username', 'tweets', 'hashtags', 'replies', 'retweets', 'likes'],
    'twitter_url': 'http://www.twitter.com/',
    'twitter_search_url': 'https://twitter.com/search?q=',
    'homepage_scroll_time': 60,
    'user_scroll_time': -1
}

if test_mode:
    scraper['homepage_scroll_time'] = 2
    scraper['user_scroll_time'] = -1

driver = 'chromedriver'

tweet = {
    'replies': 0,
    'retweets': 1,
    'likes': 2
}

mysql = {'user': 'twitter',
         'password': 'twittertwitter',
         'host': '127.0.0.1',
         'port': 3306
         }

API = {
    'consumer_key': 'dYgo8B2sDLruMrVXR0Kd7Tp5N',
    'consumer_secret': '5Yb6v2v4Y4zulq8fXL5iRuuTK4G0df48AoQI36B7XTm0cw1sIT',
    'access_token': '1204735114581827585-OLFpb3m4IHKmRlZ0kQM1j5LMRhNCyB',
    'access_token_secret': 'JXQcqSP15ihwjYDzyub9sWJFRwIjuUolhlSOlj5IlhjkP'
}

coin = {
    'price_hist_url':'https://www.bitstamp.net/api/v2/ticker/'
}

coin_tickers = {
    'bitcoin':'BTC',
    'ethereum':'ETH',
    'litecoin':'LTC'
}

database_name = 'twitter'
