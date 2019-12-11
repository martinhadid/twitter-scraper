from tweepy import User as tpUser
from user import User


def from_api_user(api_user):
    username = api_user.screen_name
    followers = api_user.followers_count
    following = api_user.friends_count
    total_tweets = api_user.statuses_count
    return User(username, followers, following, total_tweets)
