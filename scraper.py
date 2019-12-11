#!usr/bin/python3
from driver import Driver
from bs4 import BeautifulSoup
from csv import DictWriter
from tweet import Tweet
from user import User
import config
import logger
import traceback
import commandline

"""global variable to log info and error to scraper_logs"""
logger = logger.Logger()


class Scraper:
    def __init__(self):
        self.cli = commandline.CommandLine()
        self.url = self.cli.configure_search()
        self.driver = Driver()

    def get_html(self, scroll_time=config.scraper['homepage_scroll_time']):
        """Extract html from the browser"""
        self.driver.scroll(self.url, scroll_time)
        return BeautifulSoup(self.driver.get_page_source(), 'html.parser')

    def get_tweets(self, soup):
        """Extract tweets from twitter's feed"""
        return soup.find_all('div', class_='content')

    def build_tweet(self, tweet_html):
        """Parse tweet information"""
        tweet = Tweet()
        try:
            tweet.enrich_tweet(tweet_html)
            self.write_tweet_csv(tweet)
        except IndexError:
            logger.error('Not a tweet ' + traceback.format_exc())
            tweet.false_tweet()
        return tweet

    def scrape_tweets(self, all_tweets):
        """Get list of parsed tweets with relevant content"""
        tweets = []
        for tweet_html in all_tweets:
            tweet = self.build_tweet(tweet_html)
            if tweet:
                tweets.append(tweet)
        return tweets

    def filter_tweets(self, tweets):
        """Filters all tweets to unique tweets to avoid database conflicts."""
        final_tweets = []
        for tweet in tweets:
            if tweet not in final_tweets:
                final_tweets.append(tweet)
        return final_tweets

    def get_usernames(self, tweets):
        """Get list of users to be scraped"""
        users = []
        for tweet in tweets:
            if tweet.username not in users:
                users.append(tweet.username)
        return users

    def scrape_user(self, html, username):
        """Get parsed info from users"""
        user = User(username)
        user.enrich_user(html)
        return user

    def user_url(self, user):
        """Get users page url"""
        return config.scraper['twitter_url'] + user

    def get_extra_usernames(self, usernames, tweets):
        """Get users from retweeted tweets"""
        all_users = self.get_usernames(tweets)
        extra_users = []
        for username in all_users:
            if username not in usernames:
                extra_users.append(username)
        return extra_users

    def create_extra_users(self, extra_usernames):
        """Get unique users to be added to the DB"""
        users = []
        if extra_usernames:
            for username in extra_usernames:
                users.append(User(username))
        return users

    def scrape_all_users(self, usernames):
        """Scrape users info"""
        i = 0
        users = []
        user_tweets = []
        for username in usernames:
            if not config.test_mode or i < 2:
                self.url = self.user_url(username)
                html = self.get_html(config.scraper['user_scroll_time'])
                users.append(self.scrape_user(html, username))
                user_tweets += self.scrape_tweets(self.get_tweets(html))
            else:
                users.append(User(username))
            i += 1
            print('At user', i, 'out of', len(usernames))
        return users, user_tweets
