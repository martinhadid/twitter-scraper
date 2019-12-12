import requests
import json
from logger import Logger

"""global variable to log info and error to scraper_logs"""
logger = Logger()


class Price:
    def __init__(self):
        self.value = None
        self.timestamp = None

    def request_price(self):
        URL = 'https://www.bitstamp.net/api/ticker/'
        try:
            r = requests.get(URL)
            bitcoindata = json.loads(r.text)
            self.value = bitcoindata['last']
            self.timestamp = bitcoindata['timestamp']
        except Exception as err:
            logger.error(err)

    def get_timestamp(self):
        return self.timestamp

    def get_price(self):
        return self.value

