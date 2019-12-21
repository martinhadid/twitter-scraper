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
        print(date)
    return dates


def main_db(db_name, tweets, users, start_date):
    """Connect to DB, use it and insert users and tweets"""
    with DatabaseManager(db_name) as db:
        db.use_db()
        new_users, updated_users = db.write_users(users)
        new_tweets, updated_tweets = db.write_tweets(tweets)

    logger.info(str(new_users) + ' new users were inserted in the database. For date: '+ start_date)
    logger.info(str(updated_users) + ' users were updated. For date: '+ start_date)
    logger.info(str(new_tweets) + ' new tweets were inserted in the database. For date: '+ start_date)
    logger.info(str(updated_tweets) + ' tweets were updated. For date: '+ start_date)


def coin_db(db_name, coin):
    """Connect to DB, use it and insert prices"""
    with DatabaseManager(db_name) as db:
        db.use_db()
        if db.price_hist_exists(coin):
            db.insert_price(coin)
            db.commit()
        else:
            db.write_price_hist(coin)
            db.commit()

    logger.info('Last price: ' + str(coin.current_price))


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

        print('Scraping from ', date_range[i], 'to', date_range[i + 1])

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
