import datetime
import json
import threading
import time

from LogConf import getLogger
from SEURobot import SEURobotFromFile

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
        logging.info("正在预约《" + lecture['JZMC'] + "》")
        data = {'paramJson': json.dumps({"HD_WID": HD_WID})}
        last_sec = datetime.datetime.now().second
        while datetime.datetime.now().minute >= 2:  # 至少要到整点后才能开始
            now_sec = datetime.datetime.now().second
            if now_sec != last_sec:
                last_sec = now_sec
                logging.info('现在是%s，还不能预约' % datetime.datetime.now())
            continue
        result = session.post(url, data, headers=headers)
        logging.info("《" + lecture['JZMC'] + "》预约结果：" + result.text)

    def _make_orders(self):
        bot = SEURobotFromFile(self.login_data_path,
                               'http://ehall.seu.edu.cn/gsapp/sys/jzxxtjapp/*default/index.do',
                               lambda x: x.find_element_by_tag_name('button'))
        data = self._fetch(bot.getRequestsSession())
        lectures = data["datas"]['hdxxxs']['rows']
        thread_list = []
        for lecture in lectures:
            if self._can_order(lecture):
                thread_list.append(
                    threading.Thread(target=self._order,
                                     args=(bot.getRequestsSession(), lecture)))
        for t in thread_list:
            t.start()
            logging.info('启动线程')
        for t in thread_list:
            t.join()

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
        while True:
            try:
                self._make_orders()
                break
            except Exception as e:
                logging.error("未知错误 %s" % e)


if __name__ == "__main__":
    lo = SEULectureOrder()
    lo.run()
    while True:
        time.sleep(1)
        now = datetime.datetime.now()
        if now.minute > 58:
            logging.info("现在是%s, 可以约了" % datetime.datetime.now())
            lo.run()
        else:
            print("现在是%s, 没到时间，等一会" % datetime.datetime.now())
            if now.minute % 10 == 0 and now.second % 10 <= 1:
                logging.info("现在是%s, 没到时间，脚本在线" % datetime.datetime.now())
