TABLES = {}

TABLES['USER'] = '''CREATE TABLE IF NOT EXISTS USER (
                            USER_CD VARCHAR(40),
                            FOLLOWERS INT,
                            FOLLOWING INT,
                            TOTAL_TWEETS INT,
                            LAST_UPD_DATE INT,
                            PRIMARY KEY(USER_CD))
                '''

TABLES['TWEET'] = '''CREATE TABLE IF NOT EXISTS TWEET (
                            TWEET_ID INT PRIMARY KEY AUTO_INCREMENT, 
                            EXTERNAL_ID BIGINT,
                            USER_CD VARCHAR(40),
                            TWEET_TEXT TEXT,
                            TIMESTAMP INT,
                            REPLIES INT,
                            RETWEETS INT,
                            LIKES INT,
                            LAST_UPD_DATE INT,
                            FOREIGN KEY (USER_CD) REFERENCES USER(USER_CD))
                '''


TABLES['HASHTAG'] = '''CREATE TABLE IF NOT EXISTS HASHTAG (
                            TWEET_ID INT,
                            HASHTAG VARCHAR(40),
                            FOREIGN KEY(TWEET_ID) REFERENCES TWEET(TWEET_ID))
                '''

TABLES['TWEET_HIST'] = '''CREATE TABLE IF NOT EXISTS TWEET_HIST (
                            TWEET_ID INT, 
                            REPLIES INT,
                            RETWEETS INT,
                            LIKES INT,
                            AS_OF_DATE INT,
                            PRIMARY KEY (TWEET_ID, AS_OF_DATE),
                            FOREIGN KEY(TWEET_ID) REFERENCES TWEET(TWEET_ID))
                '''

TABLES['USER_HIST'] = '''CREATE TABLE IF NOT EXISTS USER_HIST (
                            USER_CD VARCHAR(40),
                            FOLLOWERS INT,
                            FOLLOWING INT,
                            TOTAL_TWEETS INT,
                            AS_OF_DATE INT,
                            PRIMARY KEY (USER_CD,AS_OF_DATE),
                            FOREIGN KEY (USER_CD) REFERENCES USER(USER_CD))
                '''
