from selenium import webdriver
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse


def default_webdriver_init():
    return webdriver.Edge(executable_path='./msedgedriver.exe')


class SEURobot:
    def __init__(self, username: str, pwssword: str, webdriver_init=default_webdriver_init):
        self.webdriver_init = webdriver_init
        login_url = "https://newids.seu.edu.cn/authserver/login"
        browser = self.webdriver_init()
        browser.get(login_url)
        u = WebDriverWait(browser, 10).until(
            lambda x: x.find_element_by_id("username"))
        u.clear()
        u.click()
        u.send_keys(username)
        p = WebDriverWait(browser, 10).until(
            lambda x: x.find_element_by_id("password"))
        p.clear()
        p.click()
        p.send_keys(pwssword)
        browser.find_element_by_class_name('auth_login_btn').submit()
        WebDriverWait(browser, 10).until(
            lambda x: x.find_element_by_class_name("auth_username"))
        self.selenium_cookies = browser.get_cookies()
        self.requests_session = requests.Session()
        for c in self.selenium_cookies:
            del c['domain']
            self.requests_session.cookies.set(c['name'], c['value'])
        browser.close()

    def open(self, url):
        browser = self.webdriver_init()
        browser.get(url)
        for cookie in self.selenium_cookies:
            browser.add_cookie(cookie)
        browser.get(url)
        return browser


if __name__ == "__main__":
    bot = SEURobot('220201857', 'YHM19980228yhm')
    browser = bot.open(
        "http://ehall.seu.edu.cn/qljfwapp2/sys/lwReportEpidemicSeu/*default/index.do")
    browser.implicitly_wait(10)
