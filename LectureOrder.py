import datetime
import random
import time
import requests
from requests.cookies import RequestsCookieJar

from selenium.webdriver.support.wait import WebDriverWait  # 等待页面加载某些元素
import json
from SEURobot import SEURobotFromFile
from LogConf import getLogger

logging = getLogger()


class SEULectureOrder:
    def __init__(self, login_data_path="loginData.txt"):
        self.common_headers = {
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36 Edg/89.0.774.68',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'http://ehall.seu.edu.cn',
            'Referer': 'http://ehall.seu.edu.cn/gsapp/sys/jzxxtjapp/*default/index.do',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6'
        }
        self.login_data_path = login_data_path
        self.ID = '201857'

    def _fetch(self, session):
        url = "http://ehall.seu.edu.cn/gsapp/sys/jzxxtjapp/modules/hdyy/hdxxxs.do"
        headers = self.common_headers.copy()
        headers['Accept'] = '*/*'
        session.headers.update(headers)
        data = {'XH': self.ID, 'pageNumber': '1', 'pageSize': '96'}
        return session.post(url, data, headers=headers).json()

    def _order(self, session, lecture):
        url = "http://ehall.seu.edu.cn/gsapp/sys/jzxxtjapp/hdyy/yySave.do"
        headers = self.common_headers.copy()
        headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
        session.headers.update(headers)
        HD_WID = lecture['WID']
        logging.info("正在预约" + lecture['JZMC'])
        data = {'paramJson': json.dumps({"HD_WID": HD_WID})}
        result = session.post(url, data, headers=headers)
        logging.info("预约结果" + result.text)

    def _can_order(self, lecture):
        if lecture['YY_WID'] is not None:
            logging.info("讲座《" + lecture['JZMC'] + '》已预约，不再重复预约')
            return False
        if "九龙湖" not in lecture['JZDD']:
            logging.info("讲座《" + lecture['JZMC'] + "》在" + lecture['JZDD'] + '，不在九龙湖，不预约')
            return False
        when = time.strptime(lecture['JZSJ'], "%Y-%m-%d %H:%M:%S")
        if when.tm_wday == time.localtime().tm_wday:
            logging.info('讲座《' + lecture['JZMC'] + '》时间是' + when + "现在是" + time.localtime() + "，时间太近不预约")
            return False
        return True

    def run(self):
        bot = SEURobotFromFile(self.login_data_path,
                               'http://ehall.seu.edu.cn/gsapp/sys/jzxxtjapp/*default/index.do',
                               lambda x: x.find_element_by_tag_name('button'))
        data = self._fetch(bot.getRequestsSession())
        lectures = data["datas"]['hdxxxs']['rows']
        for lecture in lectures:
            if self._can_order(lecture):
                self._order(bot.getRequestsSession(), lecture)


if __name__ == "__main__":
    lecture = SEULectureOrder()
    print(lecture.run())
