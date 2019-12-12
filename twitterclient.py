import tweepy
from tweepy import OAuthHandler
import config
from user import User
import logger

"""global variable to log info and error to scraper_logs"""
logger = logger.Logger()


class TwitterClient:

    def __init__(self):
        '''API connector'''
        self._consumer_key = config.API['consumer_key']
        self._consumer_secret = config.API['consumer_secret']
        self._access_token = config.API['access_token']
        self._access_token_secret = config.API['access_token_secret']

        try:
            '''API Authentication'''
            self.auth = OAuthHandler(self._consumer_key, self._consumer_secret)
            self.auth.set_access_token(self._access_token, self._access_token_secret)
            self.api = tweepy.API(self.auth, wait_on_rate_limit=False)
        except Exception:
            logger.error('Authentication Failed')

    def get_users_missing_data(self, users):
        '''Main function to fetch users and complete missing data.'''
        try:
            users_with_data = []
            for user in users:
                user_data = self.api.get_user(id=user)
                users_with_data.append(
                    User(user, user_data.followers_count, user_data.friends_count, user_data.statuses_count))
            return users_with_data

        except tweepy.TweepError as err:
            logger.error('Error : ' + str(err))

    # def translate_users(self, users):
    #     new_users = []
    #     for user in users:
    #         new_users.append(User(user))

    def get_followers(self, account_name):
        """Return a list of all the followers of an account"""
        followers = []
        for page in tweepy.Cursor(self.api.followers, screen_name=str(account_name)).pages():
            followers.extend(page)
            print(len(followers))
        return followers

    def get_follower_ids(self, target):
        followers = []
        for page in tweepy.Cursor(self.api.followers(target)).pages():
            followers += page
        return followers


    # Twitter API allows us to batch query 100 accounts at a time
    # So we'll create batches of 100 follower ids and gather Twitter User objects for each batch
    def get_user_objects(self, follower_ids):
        batch_len = 100
        num_batches = len(follower_ids) / 100
        batches = (follower_ids[i:i + batch_len] for i in range(0, len(follower_ids), batch_len))
        all_data = []
        for batch_count, batch in enumerate(batches):
            print("\r")
            print("Fetching batch: " + str(batch_count) + "/" + str(num_batches))
            users_list = self.api.lookup_users(user_ids=batch)
            all_data += users_list
        return all_data


def main():
    tw = TwitterClient()
    btc_f = tw.get_follower_ids('Bitcoin')
    btc_f = tw.get_user_objects(btc_f)
    print(len(btc_f))





if __name__ == '__main__':
    main()
