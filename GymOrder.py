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

date_list = {
    '1': '周一',
    '2': '周二',
    '3': '周三',
    '4': '周四',
    '5': '周五',
    '6': '周六',
    '7': '周日',
}

time_list_weekday = {
    '1': '11:30-12:30',
    '2': '12:30-13:30',
    '3': '18:00-19:00',
    '4': '19:00-20:00',
    '5': '20:00-21:00',
}

time_list_weekend = {
    '1': '09:00-10:00',
    '2': '10:00-11:00',
    '3': '11:00-12:00',
    '4': '12:00-13:00',
    '5': '13:00-14:00',
    '6': '14:00-15:00',
    '7': '15:00-16:00',
    '8': '16:00-17:00',
    '9': '17:00-18:00',
    '10': '18:00-19:00',
}

time_list = {
    '1': time_list_weekday,
    '2': time_list_weekday,
    '3': time_list_weekday,
    '4': time_list_weekday,
    '5': time_list_weekday,
    '6': time_list_weekend,
    '7': time_list_weekend,
}


class SEUGymOrder:
    def __init__(self, time_config, get_seubot):
        self.get_seubot = get_seubot
        self.bot = None
        self.validateimage_url = "http://yuyue.seu.edu.cn:80/eduplus/control/validateimage"
        self.order_url = "http://yuyue.seu.edu.cn/eduplus/order/order/order/insertOredr.do?sclId=1"
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
        session = self.bot.getRequestsSession()
        headers = self.headers.copy()
        headers["Referer"] = self.validateimage_url
        response = session.get(self.validateimage_url, headers=headers)
        return str(getResutlFromBuffer(response.content))

    def login(self):
        self.bot = self.get_seubot()

    def make_orders(self):
        session = self.bot.getRequestsSession()
        for pdg in self.post_data_gen:
            validate_code = self.getValidateCode()
            post_data = pdg(validate_code)
            session.post(self.order_url, data=post_data)

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
