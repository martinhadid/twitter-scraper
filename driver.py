from selenium import webdriver
import os
import time
import config


class Driver:
    def __init__(self):
        self.driver = webdriver.Chrome(os.path.join(os.path.dirname(__file__), config.driver))

    def scroll(self, url, max_time=2):
        """
        Scroll down the browser for the requested time
        :param url: url to be requested
        :param max_time: amount of time to be scrolling
        """
        self.driver.get(url)
        start_time = time.time()
        while (time.time() - start_time) < max_time:
            self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            print(str(time.time() - start_time) + ' < ' + str(max_time))

    def get_page_source(self):
        """
        Get page source from the browser
        :return: page source to be scraped
        """
        return self.driver.page_source

    def quit(self):
        """
        Close the browser
        """
        self.driver.quit()
