import datetime
import json
import logging
import threading
import time

import requests
from selenium.webdriver.support.wait import WebDriverWait  # 等待页面加载某些元素

from PicProcess import getResutlFromBuffer
from SEURobot import SEURobot, SEURobotFromFile

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
    def __init__(self, order_list, bot: SEURobot):
        self.order_list = order_list
        self.headers = {
            'Accept': 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Connection': 'keep-alive',
            'Host': 'yuyue.seu.edu.cn',
            'Referer': 'http://yuyue.seu.edu.cn/eduplus/order/order/initEditOrder.do?sclId=1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36 Edg/89.0.774.54',
        }
        self.url_format = 'http://yuyue.seu.edu.cn/eduplus/order/initEditOrder.do?sclId=1&dayInfo=%s&itemId=10&time=%s'
        self.validateimage_url = "http://yuyue.seu.edu.cn:80/eduplus/control/validateimage"
        self.bot = bot
        self.lock = threading.Lock()

    def getValidateCode(self, browser, url):
        requests_session = requests.Session()
        for cookie in browser.get_cookies():
            requests_session.cookies.set(cookie['name'], cookie['value'])
        self.headers["Referer"] = url
        response = requests_session.get(self.validateimage_url, headers=self.headers)
        return str(getResutlFromBuffer(response.content))

    def _make_order(self, url):
        while datetime.datetime.now().hour < 8:  # 至少要到8点后才能开始
            logging.info('现在是%s，还不能预约' % datetime.datetime.now())
            continue
        logging.info('现在是%s，可以开始预约' % datetime.datetime.now())
        browser = self.bot.open(url)
        validateCode = WebDriverWait(browser, 10).until(
            lambda x: x.find_element_by_id('validateCode'))
        self.lock.acquire()
        validateCode.clear()
        validateCode.click()
        validateCode.send_keys(self.getValidateCode(browser, url))
        browser.execute_script("submit()")
        time.sleep(2)
        self.lock.release()
        now = datetime.datetime.now()
        fname = now.strftime("%Y%m%d-%H.%M.%S.") + str(now.microsecond)
        browser.get_screenshot_as_file("screenshots/" + fname + '.png')
        browser.close()

    def _make_orders(self):
        thread_list = []
        for order in self.order_list:
            date, t = str(order[0]), str(order[1])
            logging.info("预约一个%s %s的场馆" % (date_list[date], time_list[date][t]))
            today = datetime.date.today()
            for i in range(1, 3):
                day = today + datetime.timedelta(days=i)
                weekday = str(day.weekday() + 1)
                if weekday == date:
                    str_day = day.strftime('%Y-%m-%d')
                    str_weekday = date_list[weekday]
                    str_time = time_list[date][t]
                    logging.info("%s是%s, 可以预约" % (str_day, str_weekday))
                    thread_list.append(
                        threading.Thread(target=self._make_order,
                                         args=(self.url_format % (str_day, str_time),)))
                    break
        for t in thread_list:
            t.start()
            logging.info('启动线程')
        for t in thread_list:
            t.join()

    def run(self):
        while True:
            try:
                self._make_orders()
                break
            except Exception as e:
                logging.error("未知错误 %s" % e)


class SEUGymOrderFromFile(SEUGymOrder):
    def __init__(self, path, bot: SEURobot):
        # 记录下要预约什么时间的场馆，以后都不用重复输入
        try:
            with open(path, mode='r', encoding='utf-8') as f:
                # 去掉换行符
                order_list = json.load(f)
                f.close()
        except FileNotFoundError:
            order_list = []
            while True:
                print('你想预约星期几的场馆？')
                for i in range(1, len(date_list) + 1):  # 输出日期列表
                    print(i, ")", date_list[str(i)])
                while True:
                    date = input('请输入数字：')
                    date = str(date)
                    if date in date_list:
                        break
                    else:
                        print('错误')
                print('你想预约哪个时间段的场馆？')
                for i in range(1, len(time_list[date]) + 1):  # 输出日期列表
                    print(i, ")", time_list[date][str(i)])
                while True:
                    time = input('请输入数字：')
                    time = str(time)
                    if time in time_list[date]:
                        break
                    else:
                        print('错误')
                order_list.append([int(date), int(time)])
                print('已添加计划：预约%s %s的场馆' %
                      (date_list[date], time_list[date][time]))
                con = input("还需要添加其他时间吗？y/N")
                if con != 'y' and con != 'Y':
                    break
            with open("orderList.json", mode='w', encoding='utf-8') as f:
                json.dump(order_list, f)
                f.close()

        logging.info('预约如下时间的场馆')
        for order in order_list:
            date, time = order
            logging.info('预约%s %s的场馆' %
                         (date_list[str(date)], time_list[str(date)][str(time)]))

        super().__init__(order_list, bot)


if __name__ == "__main__":
    logging.basicConfig(filename='logs/gym-log-%s.log' % time.strftime("%Y-%m-%d", time.localtime()),
                        format='%(asctime)s\t%(levelname)s\t%(filename)s:%(lineno)d\t%(message)s', level=logging.DEBUG,
                        filemode='a', datefmt='%I:%M:%S %p')
    go = SEUGymOrderFromFile("orderList.json", SEURobotFromFile("loginData.txt"))
    go.run()
    while True:
        time.sleep(1)
        now = datetime.datetime.now()
        if now.hour > 7 and  now.hour < 16 and now.minute > 58:
            logging.info("现在是%s, 可以约了" % datetime.datetime.now())
            go.run()
        else:
            print("现在是%s, 没到时间，等一会" % datetime.datetime.now())
            if now.minute % 10 == 0:
                logging.info("现在是%s, 没到时间，脚本在线" % datetime.datetime.now())
