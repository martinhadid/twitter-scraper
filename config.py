test_mode = False

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

database_name = 'twitter'