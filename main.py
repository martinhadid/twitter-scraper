from databasemanager import DatabaseManager
from mysql import connector
from logger import Logger
import config
from commandline import CommandLine
from driver import Driver
from scraper import Scraper
from twitterclient import TwitterClient
from price import Price
import ssl


"""global variable to log info and error to scraper_logs"""
logger = Logger()


def main_db(db_name, tweets, users, price):
    """Create DB, use it and insert users, tweets and price"""
    with DatabaseManager(db_name) as db:
        db.use_db()
        new_users, updated_users = db.write_users(users)
        db.commit()
        new_tweets, updated_tweets = db.write_tweets(tweets)
        db.commit()
        db.insert_price(price)
        db.commit()

    logger.info(str(new_users) + ' new users were inserted in the database. ')
    logger.info(str(updated_users) + ' users were updated.')
    logger.info(str(new_tweets) + ' new tweets were inserted in the database. ')
    logger.info(str(updated_tweets) + ' tweets were updated.')
    logger.info('Last price: ' + str(price.get_price()))


def main():
    cli = CommandLine()
    url = cli.configure_search()

    price = Price()
    # Avoid untrusted ssl certificates issues
    ssl._create_default_https_context = ssl._create_unverified_context
    price.request_price()
    price.get_hist_price(cli.get_start_date(), cli.get_end_date())

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
        main_db(config.database_name, tweets, users, price)
        driver.quit()

    except connector.errors.ProgrammingError:
        logger.error('DB doesn\'t exists, please run create_db.sql')
    except connector.errors.DatabaseError:
        logger.error('Can\'t connect to server')
    except Exception:
        logger.error('Something went wrong!')
        driver.quit()


if __name__ == '__main__':
    main()
