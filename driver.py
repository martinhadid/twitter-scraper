from selenium import webdriver
import os
import time


class Driver:
    def __init__(self):
        self.driver = webdriver.Chrome(os.path.dirname(__file__) + '/chromedriver')

    def scroll(self, url, max_time=2):
        self.driver.get(url)
        start_time = time.time()
        while (time.time() - start_time) < max_time:
            self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            print(str(time.time() - start_time) + ' < ' + str(max_time))

    def get_page_source(self):
        return self.driver.page_source

    def quit(self):
        self.driver.quit()
