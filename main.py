from databasemanager import DatabaseManager
from mysql import connector
from logger import Logger
import config
from commandline import CommandLine
from driver import Driver
from scraper import Scraper
from twitterclient import TwitterClient
from coin import Coin
import ssl
import tweepy
from datetime import datetime
from datetime import timedelta
import traceback
from database_utilities import *

"""global variable to log info and error to scraper_logs"""
logger = Logger()

# Avoid untrusted ssl certificates issues
ssl._create_default_https_context = ssl._create_unverified_context


def configure_search(cli, start_date, end_date):
    """Prepares the Url to be requested"""
    url = config.scraper['twitter_search_url']
    url += '%23{}%20'.format(cli.coin)
    url += 'since%3A{}%20until%3A{}&'.format(start_date, end_date)
    url += 'l={}&'.format(cli.language)
    url += 'src=typd'
    return url


def get_date_range(cli):
    """Gets range of dates to be scraped"""
    date = cli.start_date
    dates = []
    while date != cli.end_date:
        dates.append(date)
        my_date = datetime.strptime(date, "%Y-%m-%d")
        date = (my_date + timedelta(days=1)).strftime("%Y-%m-%d")
    return dates


def main_coin(cli):
    """Generate coin instance"""
    coin = Coin(config.coin_tickers[cli.coin])
    coin.get_current_price()
    coin.set_hist_price(cli.start_date, cli.end_date)
    return coin


def main():
    cli = CommandLine()

    date_range = get_date_range(cli)

    coin = main_coin(cli)
    coin_db(config.database_name, coin)

    for i in range(len(date_range) - 1):

        url = configure_search(cli, date_range[i], date_range[i + 1])

        logger.info('Scraping from ' + str(date_range[i]) +  'to' +str(date_range[i + 1]))

        driver = Driver()
        scraper = Scraper(driver, url)
        twitter_client = TwitterClient()

        try:
            # First we scrape the site for TWEETS and USERS.
            tweets, users = scraper.scrape()
            # Retweeted tweet's original users are not handled by the scraper and will have incomplete info:
            extra_usernames = scraper.get_extra_usernames(users, tweets)
            # We complete these with the API
            users += twitter_client.get_users_missing_data(extra_usernames)
            # Save to DB
            main_db(config.database_name, tweets, users, date_range[i])

        except connector.errors.ProgrammingError:
            logger.error('DB doesn\'t exists, please run create_db.sql')
        except connector.errors.DatabaseError:
            logger.error('Can\'t connect to server')
        except tweepy.error.RateLimitError:
            logger.error('Twitter API rate limit exceeded.')
        except Exception:
            logger.error('Something went wrong!' + traceback.format_exc())

        driver.quit()


if __name__ == '__main__':
    main()
