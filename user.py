class User:
    def __init__(self, username, followers=None, following=None, total_tweets=None):
        self.username = username
        self.followers = followers
        self.following = following
        self.total_tweets = total_tweets

    def __eq__(self, other):
        if self.username == other.username:
            return True
        else:
            return False

    def __bool__(self):
        if self.followers is None and self.following is None and self.total_tweets is None:
            return False
        else:
            return True

    def _fetch_stats(self, scrap):
        """Fetches user stats and adds these to user object."""
        all_stats = scrap.find_all('a', class_='ProfileNav-stat')
        stats_dict = {}
        for stat in all_stats:
            if 'data-count' in stat.find('span', class_="ProfileNav-value").attrs:
                stats_dict[stat.attrs['data-nav']] = stat.find('span', class_="ProfileNav-value").attrs['data-count']
        if 'followers' in stats_dict:
            self.followers = stats_dict['followers']
        if 'following' in stats_dict:
            self.following = stats_dict['following']
        if 'tweets' in stats_dict:
            self.total_tweets = stats_dict['tweets']

    def enrich_user(self, scrap):
        """Scraps users and enriches the object"""
        self._fetch_stats(scrap)
