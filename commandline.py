import config
import argparse


class CommandLine:
    def __init__(self):
        self.argparser = self.get_argparser()
        self.coin = self.argparser['coin']
        self.start_date = self.argparser['start_date']
        self.end_date = self.argparser['end_date']
        self.language = self.argparser['language']
        self.configure_search()

    def get_argparser(self):
        """Command line interface configuration handler"""
        parser = argparse.ArgumentParser(description='Command Configuration')
        parser.add_argument('--coin', choices=['bitcoin', 'ethereal', 'litecoin'], default='bitcoin')
        parser.add_argument('--start_date', default='2019-10-21')
        parser.add_argument('--end_date', default='2019-10-31')
        parser.add_argument('--language', choices=['en', 'it', 'es', 'fr', 'de', 'ru', 'zh'], default='en')

        argparser = parser.parse_args()
        return argparser.__dict__

    def configure_search(self):
        """Prepares the Url to be requested"""
        url = config.scraper['twitter_search_url']
        url += '%23{}%20'.format(self.coin)
        url += 'since%3A{}%20until%3A{}&'.format(self.start_date, self.end_date)
        url += 'l={}&'.format(self.language)
        url += 'src=typd'
        return url

    def get_start_date(self):
        return self.start_date

    def get_end_date(self):
        return self.end_date
