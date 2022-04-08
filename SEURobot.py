import requests
from selenium.webdriver.support.ui import WebDriverWait

from driver_config import webdriver_init as webdriver_init


class SEURobot:
    def __init__(self, username: str, password: str,
                 login_url="https://newids.seu.edu.cn/authserver/login",
                 success_lambda=lambda x: x.find_element_by_class_name("auth_username")):
        self.webdriver_init = webdriver_init
        self.username = username
        self.password = password
        self.login_url = login_url
        self.success_lambda = success_lambda
        self._getCookies()

    def _getCookies(self):
        browser = self.webdriver_init()
        browser.get(self.login_url)
        u = WebDriverWait(browser, 10).until(
            lambda x: x.find_element_by_id("username"))
        u.clear()
        u.click()
        u.send_keys(self.username)
        p = WebDriverWait(browser, 10).until(
            lambda x: x.find_element_by_id("password"))
        p.clear()
        p.click()
        p.send_keys(self.password)
        browser.find_element_by_class_name('auth_login_btn').submit()
        WebDriverWait(browser, 10).until(self.success_lambda)
        self.selenium_cookies = browser.get_cookies()
        browser.close()

    def open(self, url):
        browser = self.webdriver_init()
        browser.get(url)
        for cookie in self.selenium_cookies:
            browser.add_cookie(cookie)
        browser.get(url)
        self.selenium_cookies = browser.get_cookies()
        return browser

    def getRequestsSession(self):
        requests_session = requests.Session()
        for c in self.selenium_cookies:
            print("Cookie: %s %s" % (c['name'], c['value']))
            requests_session.cookies.set(c['name'], c['value'])
        return requests_session

if __name__ == "__main__":
    from login_config import username, password

    bot = SEURobot(username, password)
    browser = bot.open(
        "http://ehall.seu.edu.cn/qljfwapp2/sys/lwReportEpidemicSeu/*default/index.do")
    print(bot.getRequestsSession())
    browser.implicitly_wait(10)
    browser.close()
