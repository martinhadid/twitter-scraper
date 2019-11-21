import os
from bs4 import BeautifulSoup
import time
from csv import DictWriter
import datetime
from selenium import webdriver
import db_tools
import sqlite3
import requests

DB_PATH = 'tweets.db'
URL = 'https://twitter.com/hashtag/bitcoin?f=tweets&vertical=default'


class User:
    def __init__(self, username, followers=None, following=None, total_tweets=None):
        self.username = username
        self.followers = followers
        self.following = following
        self.total_tweets = total_tweets

    def _fetch_stats(self, scrap):
        all_stats = scrap.find_all('a', class_='ProfileNav-stat')
        stats_dict = {}
        for stat in all_stats:
            if 'data-nav' in stat.attrs:
                stats_dict[stat.attrs['data-nav']] = stat.find('span', class_="ProfileNav-value").attrs['data-count']
        self.followers = stats_dict['followers']
        self.following = stats_dict['following']
        self.total_tweets = stats_dict['tweets']

    def enrich_user(self, scrap):
        self._fetch_stats(scrap)


def init_driver():
    directory = os.path.dirname(__file__)
    chrome_driver_path = directory + '/chromedriver'
    driver = webdriver.Chrome(chrome_driver_path)
    return driver


def scroll(driver, url=URL, max_time=.5):
    driver.get(url)
    start_time = time.time()  # remember when we started
    while (time.time() - start_time) < max_time:
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        print(str(time.time() - start_time) + ' < ' + str(max_time))


def scrape_user(driver, username):
    try:
        tweet_divs = driver.page_source
        soup = BeautifulSoup(tweet_divs, 'html.parser')
        user = User(username)
        user.enrich_user(soup)
        db_tools.insert_user(user, DB_PATH)
    except IndexError as e:
        print('Something went wrong!')
        print(e)
        driver.quit()


def main():
    driver = init_driver()
    users = ['Bitcoin', 'BlazzordDGB']
    db_tools.delete_db(DB_PATH)
    db_tools.create_db_tables(DB_PATH)
    for user in users:
        url = 'http://www.twitter.com/' + user
        scroll(driver, url, 1)
        scrape_user(driver, user)
    driver.quit()


if __name__ == '__main__':
    main()
