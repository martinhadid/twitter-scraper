#!usr/bin/python3
from driver import Driver
from bs4 import BeautifulSoup
from csv import DictWriter
import argparse
import db_tools
from tweet import Tweet
from user import User
import datetime

DB_PATH = 'tweets.db'
CSV_HEADERS = ['tweet_id', 'date', 'username', 'tweets', 'hashtags', 'replies', 'retweets', 'likes']
TWITTER_BASE_URL = 'http://www.twitter.com/'


def get_html(driver):
    page_source = driver.get_page_source()
    soup = BeautifulSoup(page_source, 'html.parser')
    return soup


def scrape_tweets(soup):
    tweets = []
    all_tweets = soup.find_all('div', class_='content')
    for tweet_html in all_tweets:
        tweet = Tweet()
        try:
            tweet.enrich_tweet(tweet_html)
            write_tweet_csv(tweet)
            tweets.append(tweet)
        except IndexError:
            print('Not a tweet')
    return tweets


def scrape_user(soup, username):
    user = User(username)
    user.enrich_user(soup)
    return user


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


def main_db():
    db_tools.delete_db(DB_PATH)
    db_tools.create_db_tables(DB_PATH)


def main():
    args = get_argparser()
    url = configure_search(args['word'], args['start_date'], args['end_date'], args['language'])

    driver = Driver()
    driver.scroll(url)

    write_csv_header()

    try:
        tweets = scrape_tweets(get_html(driver))
        usernames = get_users(tweets)
    except Exception as e:
        print('Something went wrong!')
        print(e)
        driver.quit()
    users = []
    print('The number of unique usernames gathered is:', len(usernames))
    i = 0
    for username in usernames[:1]:
        print('**********\nWere at user', i, 'out of', len(usernames), '\n******')
        url = user_url(username)
        driver.scroll(url, .5)
        users.append(scrape_user(get_html(driver), username))
        tweets += scrape_tweets(get_html(driver))
        i += 1

    main_db()
    init_time = datetime.datetime.timestamp(datetime.datetime.now())
    tweets_added = db_tools.write_tweets(tweets, init_time, DB_PATH)
    print('A total of', tweets_added, 'were added to DB.')
    users_added = db_tools.write_users(users, init_time, DB_PATH)
    print('A total of', users_added, 'users were added to DB.')
    print('The tweets are ready!')
    driver.quit()


if __name__ == '__main__':
    main()
