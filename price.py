import requests
import json
from logger import Logger
from yahoofinancials import YahooFinancials

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

    def get_hist_price(self, start_date, end_date):
        fin = YahooFinancials('BTCUSD=X')
        prices = fin.get_historical_price_data(start_date, end_date, 'daily')
        price_per_day = {}

        for value in prices['BTCUSD=X']['prices']:
            price_per_day[value['date']] = value['close']

        print(price_per_day)
        return price_per_day

    def get_timestamp(self):
        return self.timestamp

    def get_price(self):
        return self.value

def calc_returns(prices):
    returns = []
    for i in range(len(prices) - 1):
        ret = (prices[i + 1] - prices[i]) / prices[i]
        returns.append(ret)
    return returns


def running_cum_return(returns, period_length):
    running_returns = []
    for i in range(len(returns) - period_length):
        running_return = 1
        for ret in returns[i:i + period_length]:
            running_return *= (1 + ret)
        running_returns.append(running_return - 1)
    return running_returns

def main():
    price = Price()
    price.get_hist_price('2019-10-21', '2019-10-31')


if __name__ == '__main__':
    main()