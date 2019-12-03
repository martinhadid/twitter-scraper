#!usr/bin/python3
from driver import Driver
from bs4 import BeautifulSoup
from csv import DictWriter
import argparse
from tweet import Tweet
from user import User
import config
from database_manager import Database_Manager
import db_queries
import logger
import traceback

logger = logger.Logger()


def get_html(driver):
    """Extract html from the browser"""
    return BeautifulSoup(driver.get_page_source(), 'html.parser')


def get_tweets(soup):
    """Extract tweets from twitter's feed"""
    return soup.find_all('div', class_='content')


def build_tweet(tweet_html):
    """Parse tweet information"""
    tweet = Tweet()
    try:
        tweet.enrich_tweet(tweet_html)
        write_tweet_csv(tweet)
    except IndexError:
        logger.error('Not a tweet ' + traceback.format_exc())
        tweet.false_tweet()
    return tweet


def scrape_tweets(all_tweets):
    """Get list of parsed tweets with relevant content"""
    tweets = []
    for tweet_html in all_tweets:
        tweet = build_tweet(tweet_html)
        if tweet:
            tweets.append(tweet)
    return tweets


def get_usernames(tweets):
    """Get list of users to be scraped"""
    users = []
    for tweet in tweets:
        if tweet.username not in users:
            users.append(tweet.username)
    return users


def scrape_user(html, username):
    """Get parsed info from users"""
    user = User(username)
    user.enrich_user(html)
    return user


def get_argparser():
    """Command line interface configuration handler"""
    parser = argparse.ArgumentParser(description='Command Configuration')
    parser.add_argument('--word', default='bitcoin')
    parser.add_argument('--start_date', default='2019-10-21')
    parser.add_argument('--end_date', default='2019-10-31')
    parser.add_argument('--language', choices=['en', 'it', 'es', 'fr', 'de', 'ru', 'zh'], default='en')

    argparser = parser.parse_args()
    return argparser.__dict__


def configure_search(word, start_date, end_date, language):
    """Prepares the Url to be requested"""
    url = config.scraper['twitter_search_url']
    url += '%23{}%20'.format(word)
    url += 'since%3A{}%20until%3A{}&'.format(start_date, end_date)
    url += 'l={}&'.format(language)
    url += 'src=typd'
    return url


def write_csv_header():
    """Writes csv columns headers"""
    with open('twitterData.csv', 'w+') as csv_file:
        writer = DictWriter(csv_file, fieldnames=config.scraper['csv_headers'])
        writer.writeheader()


def write_tweet_csv(tweet):
    """Writes down the tweet info into a csv"""
    with open('twitterData.csv', 'a+', encoding='utf-8') as csv_file:
        writer = DictWriter(csv_file, fieldnames=config.scraper['csv_headers'])
        writer.writerow({'tweet_id': tweet.tweet_id,
                         'date': tweet.date,
                         'username': tweet.username,
                         'tweets': tweet.text,
                         'hashtags': ' '.join(tweet.hashtags),
                         'replies': tweet.replies,
                         'retweets': tweet.retweets,
                         'likes': tweet.likes})


def user_url(user):
    """Get users page url"""
    return config.scraper['twitter_url'] + user


def filter_tweets(tweets):
    """Filters all tweets to unique tweets to avoid database conflicts."""
    final_tweets = []
    for tweet in tweets:
        if tweet not in final_tweets:
            final_tweets.append(tweet)
    return final_tweets


def get_extra_usersnames(usernames, tweets):
    all_users = get_usernames(tweets)
    extra_users = []
    for username in all_users:
        if username not in usernames:
            extra_users.append(username)
    return extra_users


def create_extra_users(extra_usernames):
    users = []
    if extra_usernames:
        for username in extra_usernames:
            users.append(User(username))
    return users


def main_db(db_name, tweets, users):
    with Database_Manager(db_name) as db:
        db.create_db()
        db.use_db()
        db.create_tables(db_queries.TABLES)
        new_users, updated_users = db.write_users(users)
        db.commit()
        new_tweets, updated_tweets = db.write_tweets(tweets)
        db.commit()
    print(new_users, 'new users were inserted in the database.', updated_users, 'users were updated.')
    print(new_tweets, 'new tweets were inserted in the database.', updated_tweets, 'tweets were updated.')
    print('The tweets are ready!')


def scrape_all_users(usernames, driver):
    i = 0
    users = []
    user_tweets = []
    for username in usernames:
        if not config.test_mode or i < 2:
            print('**********\nWere at user', i, 'out of', len(usernames), '\n******')
            url = user_url(username)
            driver.scroll(url, .5)
            users.append(scrape_user(get_html(driver), username))
            user_tweets += scrape_tweets(get_tweets(get_html(driver)))
        else:
            users.append(User(username))
        i += 1
    return users, user_tweets


def main():
    args = get_argparser()
    url = configure_search(args['word'], args['start_date'], args['end_date'], args['language'])

    driver = Driver()
    driver.scroll(url)

    write_csv_header()

    try:
        tweets = scrape_tweets(get_tweets(get_html(driver)))
    except Exception:
        logger.error('Something went wrong! ' + traceback.format_exc())
        driver.quit()
    finally:
        usernames = get_usernames(tweets)
        users, user_tweets = scrape_all_users(usernames, driver)
        tweets += user_tweets
        extra_usernames = get_extra_usersnames(usernames, tweets)
        users += create_extra_users(extra_usernames)

        tweets = filter_tweets(tweets)

        main_db(config.database_name, tweets, users)
        driver.quit()


if __name__ == '__main__':
    main()
