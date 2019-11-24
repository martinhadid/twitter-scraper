#!usr/bin/python3
from driver import Driver
from bs4 import BeautifulSoup
import time
from csv import DictWriter
import argparse
import db_tools
from tweet import Tweet
from user_data import User
import datetime

DB_PATH = 'tweets.db'
CSV_HEADERS = ['tweet_id', 'date', 'username', 'tweets', 'hashtags', 'replies', 'retweets', 'likes']
TWITTER_BASE_URL = 'http://www.twitter.com/'


def scrape_tweets(driver):
    try:
        tweet_divs = driver.page_source
        soup = BeautifulSoup(tweet_divs, 'html.parser')
        all_tweets = soup.find_all('div', class_='content')
        tweets = []
        # print(all_tweets)
        for tweet_html in all_tweets:
            tweet = Tweet()
            try:
                tweet.enrich_tweet(tweet_html)
                write_tweet_csv(tweet)
                tweets.append(tweet)
            except IndexError:
                print('Not a tweet')
        return tweets
    except Exception as e:
        print('Something went wrong!')
        print(e)
        driver.quit()


def scrape_user(driver, username):
    try:
        user_divs = driver.page_source
        soup = BeautifulSoup(user_divs, 'html.parser')
        user = User(username)
        user.enrich_user(soup)
        return user
    except IndexError as e:
        print('Something went wrong!')
        print(e)
        driver.quit()


def get_users(tweets):
    users = []
    for tweet in tweets:
        if tweet.username not in users:
            users.append(tweet.username)
    return users


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


def user_url(user):
    return TWITTER_BASE_URL + user


def main():
    args = get_argparser()
    url = configure_search(args['word'], args['start_date'], args['end_date'], args['language'])
    driver = Driver().create()
    scroll(driver, url, 5)
    init_time = datetime.datetime.timestamp(datetime.datetime.now())
    write_csv_header()
    db_tools.delete_db(DB_PATH)
    db_tools.create_db_tables(DB_PATH)
    tweets = scrape_tweets(driver)
    usernames = get_users(tweets)
    users = []
    print('The number of unique usernames gathered is:', len(usernames))
    i = 0
    for username in usernames[:1]:
        print('**********\nWere at user', i, 'out of', len(usernames), '\n******')
        url = user_url(username)
        scroll(driver, url, .5)
        users.append(scrape_user(driver, username))
        tweets += scrape_tweets(driver)
        i += 1

    tweets_added = db_tools.write_tweets(tweets, init_time, DB_PATH)
    print('A total of', tweets_added, 'were added to DB.')
    users_added = db_tools.write_users(users, init_time, DB_PATH)
    print('A total of', users_added, 'users were added to DB.')
    time.sleep(5)
    print('The tweets are ready!')
    driver.quit()


if __name__ == '__main__':
    main()
