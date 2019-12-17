from selenium import webdriver
import os
import time
import config
from selenium.webdriver.chrome.options import Options


class Driver:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        self.driver = webdriver.Chrome(os.path.join(os.path.dirname(__file__), config.driver), chrome_options=chrome_options)

    def scroll(self, url, max_time):
        """Scroll down the browser for the requested time"""
        self.driver.get(url)
        start_time = time.time()
        if not max_time == -1:
            while (time.time() - start_time) < max_time:
                self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')

    def get_page_source(self):
        """Get page source from the browser"""
        return self.driver.page_source

    def quit(self):
        """Close the browser"""
        self.driver.quit()
