import logging


class Logger:
    def __init__(self):
        self.logger = logging.getLogger('TwitterLogger')
        self.fh = logging.FileHandler('scraper_logs.log')
        self.set_level()
        self.set_formatter()
        self.add_handler()

    def set_level(self):
        self.logger.setLevel(logging.DEBUG)

    def set_formatter(self):
        self.fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    def add_handler(self):
        self.logger.addHandler(self.fh)

    def error(self, message):
        self.logger.error(message)
