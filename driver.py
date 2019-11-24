from selenium import webdriver
import os


class Driver:
    def __init__(self):
        self.driver = webdriver.Chrome(os.path.dirname(__file__) + '/chromedriver')

    def create(self):
        return self.driver

    def quit(self):
        self.quit()
