import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait


def default_webdriver_init():
    return webdriver.Edge(executable_path='./msedgedriver.exe')


class SEURobot:
    def __init__(self, username: str, password: str,
                 login_url="https://newids.seu.edu.cn/authserver/login",
                 success_lambda=lambda x: x.find_element_by_class_name("auth_username"),
                 webdriver_init=default_webdriver_init):
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
            requests_session.cookies.set(c['name'], c['value'])
        return requests_session


class SEURobotFromFile(SEURobot):
    def __init__(self, path: str,
                 login_url="https://newids.seu.edu.cn/authserver/login",
                 success_lambda=lambda x: x.find_element_by_class_name("auth_username")):
        try:
            with open(path, mode='r', encoding='utf-8') as f:
                # 去掉换行符
                username = f.readline().strip()
                password = f.readline().strip()
                f.close()
        except FileNotFoundError:
            with open(path, mode='w', encoding='utf-8') as f:
                username = input('Please Enter Your Username: ')
                password = input('Then Please Enter Your Password: ')
                f.write(username + '\n')
                f.write(password + '\n')
                f.close()
        super().__init__(username, password, login_url, success_lambda)


if __name__ == "__main__":
    bot = SEURobotFromFile('loginData.txt')
    browser = bot.open(
        "http://ehall.seu.edu.cn/qljfwapp2/sys/lwReportEpidemicSeu/*default/index.do")
    browser.implicitly_wait(10)
    browser.close()
