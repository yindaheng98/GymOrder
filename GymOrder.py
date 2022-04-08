import datetime
import threading
import time
from selenium.webdriver.support.ui import WebDriverWait

from PicProcess import getResutlFromBuffer
from logger import logger

logging = logger


class SEUGymOrder:
    def __init__(self, time_config, get_seubot):
        self.bot = get_seubot()
        self.session = self.bot.getRequestsSession()
        self.validateimage_url = "http://yuyue.seu.edu.cn:80/eduplus/validateimage"
        self.order_url = "http://yuyue.seu.edu.cn/eduplus/order/order/order/judgeUseUser.do?sclId=1"
        self.cookie_refresher = "http://yuyue.seu.edu.cn/eduplus/order/fetchMyOrders.do?sclId=1"
        self.headers = {
            'Accept': 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Connection': 'keep-alive',
            'Host': 'yuyue.seu.edu.cn',
            'Referer': 'http://yuyue.seu.edu.cn/eduplus/order/order/initEditOrder.do?sclId=1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36 Edg/89.0.774.54',
        }
        
        url_f = "http://yuyue.seu.edu.cn/eduplus/order/initEditOrder.do?sclId=1&dayInfo=%s&itemId=10&time=%s"
        self.page_urls = [(url_f % t) for t in time_config]

        self.browsers = {}

    def getValidateCode(self):
        headers = self.headers.copy()
        response = self.session.get(self.validateimage_url, headers=headers)
        return str(getResutlFromBuffer(response.content))

    def login(self):
        browser = self.bot.open(self.cookie_refresher)
        self.session = self.bot.getRequestsSession()

    def open_order(self, page_url):
        browser = self.bot.open(page_url)
        WebDriverWait(browser, 10).until(
            lambda x: x.find_element_by_id('validateCode')
        )
        self.browsers[page_url] = browser

    def make_order(self, page_url, validate_code):
        browser = self.browsers[page_url]
        validateCode = browser.find_element_by_id('validateCode')
        validateCode.clear()
        validateCode.click()
        validateCode.send_keys(str(validate_code))
        browser.execute_script("submit()")
        browser.get_screenshot_as_file("screenshots/"+fname+'.png')
        del browsers[page_url]

    def make_orders(self):
        for page_url in self.page_urls:
            self.open_order(page_url)
            validate_code = self.getValidateCode()
            self.make_order(page_url, validate_code)

    def run(self):
        while True:
            try:
                self.login()
                self.make_orders()
                break
            except Exception as e:
                logging.error("出错了: %s" % e)


if __name__ == "__main__":
    from SEURobot_config import get_seubot
    from time_config import time_config

    go = SEUGymOrder(time_config, get_seubot)
    go.run()
