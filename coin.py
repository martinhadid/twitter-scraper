import requests
import json
import config
from logger import Logger
from yahoofinancials import YahooFinancials

"""global variable to log info and error to scraper_logs"""
logger = Logger()


def calc_returns(prices):
    """Given prices, calculates returns"""
    returns = []
    for i in range(len(prices) - 1):
        ret = (prices[i + 1] - prices[i]) / prices[i]
        returns.append(ret)
    return returns


def get_cumulative_returns(returns, period_length):
    """Given price returns, calculates cumulative returns for analysis"""
    running_returns = []
    for i in range(len(returns) - period_length):
        running_return = 1
        for ret in returns[i:i + period_length]:
            running_return *= (1 + ret)
        running_returns.append(running_return - 1)
    return running_returns


class Coin:
    def __init__(self, ticker):
        if 'USD' in ticker:
            self.ticker = ticker
        else:
            self.ticker = ticker + 'USD'
        self.get_current_price()

    def get_current_price(self):
        """Function to get btc price"""
        URL = config.coin['price_hist_url'] + self.ticker.lower()
        try:
            r = requests.get(URL)
            data = json.loads(r.text)
            value = data['last']
            timestamp = data['timestamp']
            self.current_price = value
            self.current_datetime = timestamp
        except Exception as err:
            logger.error(err)

    def get_hist_price(self, start_date, end_date):
        """Function to get btc price between dates"""
        fin = YahooFinancials(self.ticker + '=X')
        prices = fin.get_historical_price_data(start_date, end_date, 'daily')
        price_per_day = {}
        for value in prices[self.ticker + '=X']['prices']:
            price_per_day[value['date']] = value['close']
        self.hist = price_per_day
