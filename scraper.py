#!usr/bin/python3
import os
from bs4 import BeautifulSoup
import time
from csv import DictWriter
import datetime
from selenium import webdriver
import argparse
import db_tools
import sqlite3

CSV_HEADERS = ['tweet_id', 'date', 'username', 'tweets', 'hashtags', 'replies', 'retweets', 'likes']
COUNTER_INDEX = {'replies': 0, 'retweets': 1, 'likes': 2}
DB_PATH = 'tweets.db'


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


def init_driver():
    directory = os.path.dirname(__file__)
    chrome_driver_path = directory + '/chromedriver'
    driver = webdriver.Chrome(chrome_driver_path)
    return driver


def scrape_tweets(driver):
    try:
        tweet_divs = driver.page_source
        soup = BeautifulSoup(tweet_divs, 'html.parser')
        all_tweets = soup.find_all('div', class_='content')
        tweets = []
        # print(all_tweets)
        for tweet_html in all_tweets:
            tweet = Tweet()
            tweet.enrich_tweet(tweet_html)
            write_tweet_csv(tweet)
            tweets.append(tweet)
        return tweets
    except Exception as e:
        print('Something went wrong!')
        print(e)
        driver.quit()


def get_argparser():
    parser = argparse.ArgumentParser(description='Command Configuration')
    parser.add_argument('--word', nargs='?', default='bitcoin')
    parser.add_argument('--start_date', nargs='?', default='2019-10-21')
    parser.add_argument('--end_date', nargs='?', default='2019-10-31')
    parser.add_argument('--language', nargs='?', choices=['en', 'it', 'es', 'fr', 'de', 'ru', 'zh'], default='en')

    argparser = parser.parse_args()
    return argparser.__dict__


def configure_search(word, start_date, end_date, language):
    url = 'https://twitter.com/search?q='
    url += '{}%20'.format(word)
    url += 'since%3A{}%20until%3A{}&'.format(start_date, end_date)
    url += 'l={}&'.format(language)
    url += 'src=typd'
    return url


def scroll(driver, url, max_time=2):
    driver.get(url)
    start_time = time.time()  # remember when we started
    while (time.time() - start_time) < max_time:
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        print(str(time.time() - start_time) + ' < ' + str(max_time))


def write_csv_header():
    with open('twitterData.csv', 'w+') as csv_file:
        writer = DictWriter(csv_file, fieldnames=CSV_HEADERS)
        writer.writeheader()


def write_tweet_csv(tweet):
    with open('twitterData.csv', 'a+', encoding='utf-8') as csv_file:
        writer = DictWriter(csv_file, fieldnames=CSV_HEADERS)
        writer.writerow({'tweet_id': tweet.tweet_id,
                         'date': tweet.date,
                         'username': tweet.username,
                         'tweets': tweet.text,
                         'hashtags': tweet.hashtags,
                         'replies': tweet.replies,
                         'retweets': tweet.retweets,
                         'likes': tweet.likes})


def main():
    args = get_argparser()
    url = configure_search(args['word'], args['start_date'], args['end_date'], args['language'])
    driver = init_driver()
    scroll(driver, url)
    write_csv_header()
    db_tools.delete_db(DB_PATH)
    db_tools.create_db_tables(DB_PATH)
    tweets = scrape_tweets(driver)
    tweets_added = 0
    for tweet in tweets:
        try:
            db_tools.insert_tweet(tweet, DB_PATH)
            db_tools.insert_hashtags(tweet, DB_PATH)
            tweets_added += 1
        except sqlite3.IntegrityError:
            print('Tweet ID', tweet.tweet_id, 'exists in DB')
    print('A total of', tweets_added, 'were added to DB.')
    time.sleep(5)
    print('The tweets are ready!')
    driver.quit()


if __name__ == '__main__':
    main()
