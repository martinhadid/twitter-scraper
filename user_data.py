class User:
    def __init__(self, username, followers=None, following=None, total_tweets=None):
        self.username = username
        self.followers = followers
        self.following = following
        self.total_tweets = total_tweets

    def _fetch_stats(self, scrap):
        all_stats = scrap.find_all('a', class_='ProfileNav-stat')
        stats_dict = {}
        for stat in all_stats:
            if 'data-count' in stat.find('span', class_="ProfileNav-value").attrs:
                stats_dict[stat.attrs['data-nav']] = stat.find('span', class_="ProfileNav-value").attrs['data-count']
        self.followers = stats_dict['followers']
        self.following = stats_dict['following']
        self.total_tweets = stats_dict['tweets']

    def enrich_user(self, scrap):
        self._fetch_stats(scrap)
