from databasemanager import DatabaseManager
from mysql import connector
import logger
import config
import commandline
from driver import Driver
from scraper import Scraper

"""global variable to log info and error to scraper_logs"""
logger = logger.Logger()


def main_db(db_name, tweets, users):
    """Create DB, use it and insert users and tweets"""
    with DatabaseManager(db_name) as db:
        db.use_db()
        new_users, updated_users = db.write_users(users)
        db.commit()
        new_tweets, updated_tweets = db.write_tweets(tweets)
        db.commit()

    logger.info(str(new_users) + ' new users were inserted in the database. ')
    logger.info(str(updated_users) + ' users were updated.')
    logger.info(str(new_tweets) + ' new tweets were inserted in the database. ')
    logger.info(str(updated_tweets) + ' tweets were updated.')


def main():
    driver = Driver()
    cli = commandline.CommandLine()
    url = cli.configure_search()

    scraper = Scraper(driver, url)

    try:
        tweets = scraper.scrape_tweets(scraper.get_tweets(scraper.get_html(1)))
        usernames = scraper.get_usernames(tweets)
        users, user_tweets = scraper.scrape_all_users(usernames)
        tweets += user_tweets
        extra_usernames = scraper.get_extra_usernames(usernames, tweets)
        users += scraper.create_extra_users(extra_usernames)
        tweets = scraper.filter_tweets(tweets)
        main_db(config.database_name, tweets, users)
        scraper.driver.quit()

    except connector.errors.ProgrammingError:
        logger.error('DB doesn\'t exists, please run create_db.sql')
    except connector.errors.DatabaseError:
        logger.error('Can\'t connect to server')
    except Exception:
        logger.error('Something went wrong!')
        scraper.driver.quit()


if __name__ == '__main__':
    main()
