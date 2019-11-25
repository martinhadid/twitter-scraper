import sqlite3
import scraper
import os
import user
import tweet
from datetime import datetime

DB_PATH = 'tweets.db'


def delete_db(path):
    """
    Function to remove database if exists.
    :param path: path of db to remove
    :return:
    """
    try:
        os.remove(path)
    except FileNotFoundError:
        print('Database specified does not exist')


def create_db_tables(path):
    """
    Function to create tables in DB specified. Creates the following tables:
    TWEETS: contains all info in tweets. ID, USER_CD, TWEET_TEXT, TIMESTAMP, REPLIES, RETWEETS AND LIKES
    HASHTAGS: contains all hashtags mentioned in tweets. Foreign key to TWEETS by tweet_id
    :param path: Path of DB.
    :return:
    """
    with sqlite3.connect(path) as con:
        cur = con.cursor()
        cur.execute('''CREATE TABLE TWEETS (
                            TWEET_ID INT PRIMARY KEY, 
                            USER_CD TEXT,
                            TWEET_TEXT TEXT,
                            TIMESTAMP INT,
                            REPLIES INT,
                            RETWEETS INT,
                            LIKES INT,
                            LAST_UPD_DATE INT,
                            FOREIGN KEY (USER_CD) REFERENCES USERS(USER_ID))
                ''')
        cur.execute('''CREATE TABLE HASHTAGS (
                            TWEET_ID INT,
                            HASHTAG TEXT,
                            FOREIGN KEY(TWEET_ID) REFERENCES TWEETS(TWEET_ID))
                ''')
        cur.execute('''CREATE TABLE USERS (
                            USER_ID TEXT,
                            FOLLOWERS INT,
                            FOLLOWING INT,
                            TOTAL_TWEETS INT,
                            LAST_UPD_DATE INT,
                            PRIMARY KEY(USER_ID))
                ''')
        cur.execute('''CREATE TABLE USERS_HIST (
                            USER_ID TEXT,
                            FOLLOWERS INT,
                            FOLLOWING INT,
                            TOTAL_TWEETS INT,
                            AS_OF_DATE INT,
                            PRIMARY KEY (USER_ID,AS_OF_DATE),
                            FOREIGN KEY (USER_ID) REFERENCES USERS(USER_ID))
                ''')
        cur.execute('''CREATE TABLE TWEETS_HIST (
                            TWEET_ID INT, 
                            REPLIES INT,
                            RETWEETS INT,
                            LIKES INT,
                            AS_OF_DATE INT,
                            PRIMARY KEY (TWEET_ID, AS_OF_DATE),
                            FOREIGN KEY(TWEET_ID) REFERENCES TWEETS(TWEET_ID))
                ''')
        con.commit()
        cur.close()


def insert_tweet(tweet, scrape_time, path):
    """
    Inserts tweets into DB
    :param scrape_time:
    :param tweet: Tweet object to be inserted
    :param path: Path of DB
    :return:
    """
    with sqlite3.connect(path) as con:
        cur = con.cursor()
        cur.execute('''INSERT INTO TWEETS (
                        TWEET_ID,
                        USER_CD,
                        TWEET_TEXT,
                        TIMESTAMP,
                        REPLIES,
                        RETWEETS,
                        LIKES,
                        LAST_UPD_DATE) VALUES (?,?,?,?,?,?,?,?)''',
                    [tweet.tweet_id,
                     tweet.username,
                     tweet.text,
                     tweet.date,
                     tweet.replies,
                     tweet.retweets,
                     tweet.likes,
                     scrape_time])
        con.commit()
        cur.close()


def insert_hashtags(tweet, path):
    """
    Function to insert hashtags into db. Inserts all hashtags in tweet to db specified in path
    :param tweet: Tweet object to get hashtags from
    :param path: DB PATH
    :return:
    """
    with sqlite3.connect(path) as con:
        cur = con.cursor()
        hasthags = tweet.hashtags.split(' ')
        for hashtag in hasthags:
            cur.execute('''INSERT INTO HASHTAGS (
                            TWEET_ID,
                            HASHTAG) VALUES (?,?)''',
                        [tweet.tweet_id,
                         hashtag])
        con.commit()
        cur.close()


def insert_user(user, scrape_time, path=DB_PATH):
    """
    Inserts user into database
    :param user: User
    :param scrape_time: time of scrape
    :param path: db path
    :return:
    """
    with sqlite3.connect(path) as con:
        cur = con.cursor()
        cur.execute('''INSERT INTO USERS (
                               USER_ID,
                               FOLLOWERS,
                               FOLLOWING,
                               TOTAL_TWEETS,
                               LAST_UPD_DATE) VALUES (?,?,?,?,?)''',
                    [user.username,
                     user.followers,
                     user.following,
                     user.total_tweets,
                     scrape_time])
        con.commit()
        cur.close()


def tweet_exists(tweet, path=DB_PATH):
    """Returns weather or not tweet exists"""
    with sqlite3.connect(path) as con:
        cur = con.cursor()
        cur.execute('''SELECT 1, TWEET_ID FROM TWEETS WHERE TWEET_ID = ?''',
                    [tweet.tweet_id])
        result = cur.fetchall()
        if not result:
            return False
        elif result[0][1] == tweet.tweet_id:
            return True
        else:
            return False


def user_exists(user, path):
    """Returns whether or not user exists in db"""
    with sqlite3.connect(path) as con:
        cur = con.cursor()
        cur.execute('''SELECT 1, USER_ID FROM USERS WHERE USER_ID = ?''',
                    [user.username])
        result = cur.fetchall()
        if not result:
            return False
        elif result[0][1] == user.username:
            return True
        else:
            return False


def write_tweet_hist(tweet, path):
    """Takes snapshot of tweet in TWEETS to TWEETS_HIST"""
    with sqlite3.connect(path) as con:
        cur = con.cursor()
        cur.execute('''INSERT INTO TWEETS_HIST (
                        TWEET_ID,
                        REPLIES,
                        RETWEETS,
                        LIKES,
                        AS_OF_DATE)  
                        SELECT TWEET_ID, REPLIES, RETWEETS, LIKES, LAST_UPD_DATE
                        FROM TWEETS
                        WHERE TWEET_ID = ?
                        ''',
                    [tweet.tweet_id])
        con.commit()
        cur.close()


def write_user_hist(user, path):
    """Takes snapshot of user in USER and writes it in USERS_HIST"""
    with sqlite3.connect(path) as con:
        cur = con.cursor()
        cur.execute('''INSERT INTO USERS_HIST (
                        USER_ID,
                        FOLLOWING,
                        FOLLOWERS,
                        TOTAL_TWEETS,
                        AS_OF_DATE)  
                        SELECT USER_ID, FOLLOWING, FOLLOWERS, TOTAL_TWEETS, LAST_UPD_DATE
                        FROM USERS
                        WHERE USER_ID = ?
                        ''',
                    [user.username])
        con.commit()
        cur.close()


def update_tweet(tweet, scrap_time, path):
    """Updates tweet statistics"""
    with sqlite3.connect(path) as con:
        cur = con.cursor()
        cur.execute('''UPDATE TWEETS 
                        SET REPLIES = ?,
                        RETWEETS = ? ,
                        LIKES = ?,
                        LAST_UPD_DATE = ?
                        WHERE TWEET_ID = ?''',
                    [tweet.replies,
                     tweet.retweets,
                     tweet.likes,
                     scrap_time,
                     tweet.tweet_id])
        con.commit()
        cur.close()


def update_user(user, scrap_time, path):
    """Updates user statistics"""
    with sqlite3.connect(path) as con:
        cur = con.cursor()
        cur.execute('''UPDATE USERS 
                        SET FOLLOWING = ?,
                        FOLLOWERS = ? ,
                        TOTAL_TWEETS = ?,
                        LAST_UPD_DATE = ?
                        WHERE USER_ID = ?''',
                    [user.following,
                     user.followers,
                     user.total_tweets,
                     scrap_time,
                     user.username])
        con.commit()
        cur.close()


def db_search(query, path):
    """Wrapper function to query db"""
    with sqlite3.connect(path) as con:
        cur = con.cursor()
        cur.execute(query)
        result = cur.fetchall()
        cur.close()
    return result


def get_tweet_text(tweet_id, path):
    """
    Returns text of tweet for validation purposes
    :param tweet_id: id of tweet to extract from DB
    :param path: DB PATH
    :return: text belonging to tweet_id from DB
    """
    with sqlite3.connect(path) as con:
        cur = con.cursor()
        cur.execute('''SELECT TWEET_TEXT FROM TWEETS
                    WHERE TWEET_ID IN (?)''',
                    [tweet_id])
        result = cur.fetchall()
        cur.close()
    return result[0][0]


def write_tweets(tweets, scrap_time, db=DB_PATH):
    """Wrapper function to write multiple tweets into db"""
    tweets_added = 0
    for tweet in tweets:
        try:
            insert_tweet(tweet, scrap_time, db)
            insert_hashtags(tweet, db)
            tweets_added += 1
        except sqlite3.IntegrityError:
            print('Tweet ID', tweet.tweet_id, 'exists in DB')
    return tweets_added


def write_users(users, scrape_time, db=DB_PATH):
    """wrapper function to write multiple users into db"""
    users_added = 0
    for user in users:
        if user_exists(user, db):
            write_user_hist(user, db)
            update_user(user, scrape_time, db)
        else:
            insert_user(user, scrape_time, db)
            users_added += 1
    return users_added


def main():
    print(db_search('SELECT * FROM USERS', DB_PATH))
    # print(user_exists(user.User('@BKBrianKelly'), DB_PATH))
    # write_user_hist(user.User('@BKBrianKelly'), DB_PATH)
    # update_user(user.User('@BKBrianKelly', 13, 14, 15), datetime.timestamp(datetime.now()), DB_PATH)
    print(db_search('SELECT * FROM USERS', DB_PATH))
    print(db_search('select * from users_hist', DB_PATH))


if __name__ == '__main__':
    main()
