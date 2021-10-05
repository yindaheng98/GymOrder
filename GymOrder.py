import datetime
import json
import threading
import time

import requests
from selenium.webdriver.support.wait import WebDriverWait  # 等待页面加载某些元素

from PicProcess import getResutlFromBuffer
from SEURobot import SEURobotFromFile
from logger import logger

logging = logger


class SEUGymOrder:
    def __init__(self, time_config, get_seubot):
        self.get_seubot = get_seubot
        self.bot = None
        self.session = None
        self.validateimage_url = "http://yuyue.seu.edu.cn:80/eduplus/control/validateimage"
        self.order_url = "http://yuyue.seu.edu.cn/eduplus/order/order/order/insertOredr.do?sclId=1"
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

        def make_post(t, validate_code):
            return {
                'orderVO.useTime': t,
                'orderVO.itemId': "10",
                'orderVO.useMode': "2",
                'orderVO.phone': "18851899135",
                'orderVO.remark': "",
                'validateCode': validate_code
            }

        self.post_data_gen = [lambda validate_code: make_post(t, validate_code) for t in time_config]
        self.lock = threading.Lock()

    def getValidateCode(self):
        headers = self.headers.copy()
        response = self.session.get(self.validateimage_url, headers=headers)
        return str(getResutlFromBuffer(response.content))

    def login(self):
        self.bot = self.get_seubot()
        self.bot.open(self.cookie_refresher)
        self.session = self.bot.getRequestsSession()

    def _make_order(self, pdg):
        validate_code = self.getValidateCode()
        post_data = pdg(validate_code)
        logger.debug("post data is :\n" + str(post_data))
        response = self.session.post(self.order_url, data=post_data)
        logger.info("response is :\n" + str(response.content.decode('utf8')))

    def make_orders(self):
        for pdg in self.post_data_gen:
            self._make_order(pdg)

    def run(self):
        while True:
            try:
                self.login()
                self.make_orders()
                break
            except Exception as e:
                logging.error("未知错误 %s" % e)


if __name__ == "__main__":
    from SEURobot_config import get_seubot
    from time_config import time_config

    go = SEUGymOrder(time_config, get_seubot)
    go.run()
    while True:
        time.sleep(1)
        now = datetime.datetime.now()
        if 7 <= now.hour <= 16 and now.minute > 58:
            logging.info("现在是%s, 可以约了" % datetime.datetime.now())
            for i in range(1, 6):
                logging.info("第%d次尝试" % i)
                go.run()
        else:
            print("现在是%s, 没到时间，等一会" % datetime.datetime.now())
            if now.minute % 10 == 0 and now.second % 10 <= 1:
                logging.info("现在是%s, 没到时间，脚本在线" % datetime.datetime.now())
