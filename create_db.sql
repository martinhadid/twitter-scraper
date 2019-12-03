drop database if exists twitter;
create schema twitter;
use twitter;

CREATE TABLE USER (
                    USER_CD VARCHAR(40),
                    FOLLOWERS INT,
                    FOLLOWING INT,
                    TOTAL_TWEETS INT,
                    LAST_UPD_DATE INT,
                    PRIMARY KEY(USER_CD)
                    );

CREATE TABLE TWEET (
                    TWEET_ID INT PRIMARY KEY AUTO_INCREMENT,
                    EXTERNAL_ID BIGINT,
                    USER_CD VARCHAR(40),
                    TWEET_TEXT TEXT,
                    TIMESTAMP INT,
                    REPLIES INT,
                    RETWEETS INT,
                    LIKES INT,
                    LAST_UPD_DATE INT,
                    FOREIGN KEY (USER_CD) REFERENCES USER(USER_CD)
                    );

CREATE TABLE HASHTAG (
                    TWEET_ID INT,
                    HASHTAG VARCHAR(40),
                    FOREIGN KEY(TWEET_ID) REFERENCES TWEET(TWEET_ID)
                    );

CREATE TABLE TWEET_HIST (
                        TWEET_ID INT,
                        REPLIES INT,
                        RETWEETS INT,
                        LIKES INT,
                        AS_OF_DATE INT,
                        PRIMARY KEY (TWEET_ID, AS_OF_DATE),
                        FOREIGN KEY(TWEET_ID) REFERENCES TWEET(TWEET_ID)
                        );

CREATE TABLE USER_HIST (
                        USER_CD VARCHAR(40),
                        FOLLOWERS INT,
                        FOLLOWING INT,
                        TOTAL_TWEETS INT,
                        AS_OF_DATE INT,
                        PRIMARY KEY (USER_CD,AS_OF_DATE),
                        FOREIGN KEY (USER_CD) REFERENCES USER(USER_CD)
                        );
