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

mysql = {
    'host': 'localhost',
    'user': 'root',
    'password': 'my secret password',
    'db': 'tweets.db'
}