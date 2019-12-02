from datetime import datetime
from mysql import connector
import config


# TODO MOVE COMMIT INSIDE WRITE TWEETS/USERS AND LIMIT BY NUMBER OF TWEETS/USERS

class Database_Manager:
    def __init__(self, database=None):
        """Initialize db instance"""
        self.database = database
        self.time = datetime.timestamp(datetime.now())

    def __enter__(self):
        """Open db connection and cursor"""
        self.con = connector.connect(**config.mysql)
        self.cur = self.con.cursor(buffered=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit db connection and cursor"""
        self.cur.close()
        self.con.close()

    def use_db(self):
        """Use database for all queries"""
        self.cur.execute("USE %s" % self.database)

    def create_tables(self, tables):
        """Create all tables if these don't exist"""
        for table_name in tables:
            self.cur.execute(tables[table_name])

    def run_query(self, query):
        """Run any select query"""
        self.cur.execute(query)
        result = []
        for item in self.cur:
            result.append(item)
        return result

    def create_db(self):
        """Creates database if it doesnt exist"""
        self.cur.execute("CREATE DATABASE IF NOT EXISTS %s DEFAULT CHARACTER SET 'utf8mb4'" % self.database)

    def user_exists(self, user):
        """Returns whether or not user exists in DB"""
        username = (user.username,)
        query = "SELECT 1 FROM USER WHERE USER_CD = %s"
        self.cur.execute(query, username)
        if not self.cur.rowcount:
            return False
        else:
            return True

    def tweet_exists(self, tweet):
        """Returns whether or not tweet exists in DB"""
        tweet_id = (tweet.tweet_id,)
        self.cur.execute("SELECT 1 FROM TWEET WHERE EXTERNAL_ID = %s", tweet_id)
        if not self.cur.rowcount:
            return False
        else:
            return True

    def insert_tweet(self, tweet):
        """Inserts tweet into database and attaches internal ID to tweet object."""
        query = '''INSERT INTO TWEET (EXTERNAL_ID, USER_CD, TWEET_TEXT, TIMESTAMP, REPLIES, RETWEETS, LIKES, 
                         LAST_UPD_DATE) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
        values = (tweet.tweet_id, tweet.username, tweet.text,
                  tweet.date, tweet.replies, tweet.retweets, tweet.likes, self.time)
        self.cur.execute(query, values)
        internal_id = self.cur.lastrowid
        tweet.set_internal_id(internal_id)

    def update_tweet(self, tweet):
        """Updates tweet statistics in DB"""
        query = '''UPDATE TWEET SET 
                        REPLIES = %s, 
                        RETWEETS = %s, 
                        LIKES = %s, 
                        LAST_UPD_DATE = %s
                    WHERE EXTERNAL_ID = %s'''
        values = (tweet.replies, tweet.retweets, tweet.likes,
                  self.time, tweet.tweet_id)
        self.cur.execute(query, values)

    def insert_user(self, user):
        """Inserts user into database"""
        query = '''INSERT INTO USER (USER_CD, FOLLOWERS, FOLLOWING, TOTAL_TWEETS, LAST_UPD_DATE) 
                    VALUES (%s, %s, %s, %s, %s)'''
        values = (user.username, user.followers, user.following, user.total_tweets, self.time)
        self.cur.execute(query, values)

    def update_user(self, user):
        """Updates user statistics in database"""
        query = '''UPDATE USER SET 
                            FOLLOWERS = %s,
                            FOLLOWING = %s, 
                            TOTAL_TWEETS = %s,
                            LAST_UPD_DATE = %s
                    WHERE USER_CD = %s'''
        values = (user.followers, user.following, user.total_tweets, self.time, user.username)
        self.cur.execute(query, values)

    def write_tweet_hist(self, tweet):
        """Writes tweet stats history"""
        query = '''INSERT INTO TWEET_HIST (TWEET_ID, REPLIES, RETWEETS, LIKES, AS_OF_DATE) 
                    SELECT TWEET_ID, REPLIES, RETWEETS, LIKES, LAST_UPD_DATE
                            FROM TWEET 
                            WHERE EXTERNAL_ID = %s'''
        values = (tweet.tweet_id,)
        self.cur.execute(query, values)

    def write_user_hist(self, user):
        """Writes user history"""
        query = '''INSERT INTO USER_HIST (USER_CD, FOLLOWERS, FOLLOWING, TOTAL_TWEETS, AS_OF_DATE) 
                    SELECT USER_CD, FOLLOWERS, FOLLOWING, TOTAL_TWEETS, LAST_UPD_DATE
                            FROM USER 
                            WHERE USER_CD = %s'''
        values = (user.username,)
        self.cur.execute(query, values)

    def insert_hashtags(self, tweet):
        """Inserts tweet hashtags into DB"""
        hasthags = tweet.hashtags
        tweet_id = tweet.internal_id
        query = '''INSERT INTO HASHTAG (TWEET_ID, HASHTAG) VALUES (%s, %s)'''
        for hashtag in hasthags:
            vals = (tweet_id, hashtag)
            self.cur.execute(query, vals)

    def commit(self):
        """Wrapping function to commit"""
        self.con.commit()

    def write_users(self, users):
        """Function that encapsulates user insert logic to DB. If user exists in the database it will write history
        and copy statistics. If it doesnt it will insert it. """
        updated = 0
        new = 0
        for user in users:
            if not self.user_exists(user):
                self.insert_user(user)
                new += 1
            else:
                self.write_user_hist(user)
                self.update_user(user)
                updated += 1
        return new, updated

    def write_tweets(self, tweets):
        """Function that encapsulates tweet insert logic to DB. If tweet exists in the database it will write history
                and copy statistics. If it doesnt it will insert it and insert its hashtags. """
        updated = 0
        new = 0
        for tweet in tweets:
            if not self.tweet_exists(tweet):
                self.insert_tweet(tweet)
                if tweet.hashtags:
                    self.insert_hashtags(tweet)
                new += 1
            else:
                self.write_tweet_hist(tweet)
                self.update_tweet(tweet)
                updated += 1
        return new, updated
