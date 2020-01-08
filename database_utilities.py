from databasemanager import DatabaseManager
from logger import Logger

logger = Logger()


def main_db(db_name, tweets, users, start_date):
    """Connect to DB, use it and insert users and tweets"""
    with DatabaseManager(db_name) as db:
        db.use_db()
        new_users, updated_users = db.write_users(users)
        new_tweets, updated_tweets = db.write_tweets(tweets)

    logger.info(str(new_users) + ' new users were inserted in the database. For date: ' + start_date)
    logger.info(str(updated_users) + ' users were updated. For date: ' + start_date)
    logger.info(str(new_tweets) + ' new tweets were inserted in the database. For date: ' + start_date)
    logger.info(str(updated_tweets) + ' tweets were updated. For date: ' + start_date)


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
