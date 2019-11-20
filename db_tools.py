import sqlite3
import scraper
import os

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
                            LIKES INT)''')
        cur.execute('''CREATE TABLE HASHTAGS (
                            TWEET_ID INT,
                            HASHTAG TEXT,
                            FOREIGN KEY(TWEET_ID) REFERENCES TWEETS(TWEET_ID))
                ''')
        con.commit()
        cur.close()


def insert_tweet(tweet, path):
    """
    Inserts tweets into DB
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
                        LIKES) VALUES (?,?,?,?,?,?,?)''',
                    [tweet.tweet_id,
                     tweet.username,
                     tweet.text,
                     tweet.date,
                     tweet.replies,
                     tweet.retweets,
                     tweet.likes])
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


def db_search(query, path):
    """Wrapper function to search tweets"""
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


def main():
    print(db_search('SELECT * FROM TWEETS ORDER BY LIKES DESC LIMIT 5', DB_PATH))
    print(db_search('SELECT HASHTAG, COUNT(*) AS TOTAL FROM HASHTAGS GROUP BY HASHTAG ORDER BY TOTAL DESC LIMIT 10', DB_PATH))


if __name__ == '__main__':
    main()
