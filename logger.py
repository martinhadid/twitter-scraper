import logging


class Logger:
    def __init__(self):
        """Initialize logger with file handler and formatter"""
        self.logger = logging.getLogger('TwitterLogger')
        self.fh = logging.FileHandler('scraper_logs.log')
        self.set_level()
        self.set_formatter()
        self.add_handler()

    def set_level(self):
        """Set logger level to debug"""
        self.logger.setLevel(logging.DEBUG)

    def set_formatter(self):
        """Set format for the logs"""
        self.fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    def add_handler(self):
        """Add handler to write in file"""
        self.logger.addHandler(self.fh)

    def error(self, message):
        """Wrapped function to log errors"""
        self.logger.error(message)

    def info(self, message):
        """Wrapped function to log info"""
        self.logger.info(message)
