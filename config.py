scraper = {
    'csv_headers': ['tweet_id', 'date', 'username', 'tweets', 'hashtags', 'replies', 'retweets', 'likes'],
    'twitter_url': 'http://www.twitter.com/'
}


driver = 'chromedriver'

tweet = {
    'replies': 0,
    'retweets': 1,
    'likes': 2
}


mysql = {'user': 'tm_dev',
         'password': 'tm_devtm_dev',
         'host': '127.0.0.1',
         #'database': 'imdb',
         'port': 3306

}