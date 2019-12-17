import config
import argparse


class CommandLine:
    def __init__(self):
        self.argparser = self.get_argparser()
        self.coin = self.argparser['coin']
        self.start_date = self.argparser['start_date']
        self.end_date = self.argparser['end_date']
        self.language = self.argparser['language']

    def get_argparser(self):
        """Command line interface configuration handler"""
        parser = argparse.ArgumentParser(description='Command Configuration')
        parser.add_argument('--coin', choices=['bitcoin', 'ethereum', 'litecoin'], default='bitcoin')
        parser.add_argument('--start_date', default='2019-10-21')
        parser.add_argument('--end_date', default='2019-10-31')
        parser.add_argument('--language', choices=['en', 'it', 'es', 'fr', 'de', 'ru', 'zh'], default='en')

        argparser = parser.parse_args()
        return argparser.__dict__

