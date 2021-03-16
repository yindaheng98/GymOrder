from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By  # 按照什么方式查找，By.ID,By.CSS_SELECTOR
from selenium.webdriver.common.keys import Keys  # 键盘按键操作
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait  # 等待页面加载某些元素
from selenium.webdriver.chrome.options import Options
import time
import random
import json
import datetime
import requests
from PicProcess import getResutlFromBuffer
import threading
# 加启动配置 禁用日志log
# ie capabilities
# capabilities = DesiredCapabilities.INTERNETEXPLORER
# capabilities.pop("platform", None)
# capabilities.pop("version", None)


url = "http://yuyue.seu.edu.cn/eduplus/order/initEditOrder.do?sclId=1&dayInfo=%s&itemId=10&time=%s"
dailyDone = False  # 今日是否已经打卡

# 创建打卡记录log文件


def writeLog(text):
    with open('log.txt', 'a') as f:
        s = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ' ' + text
        print(s)
        f.write(s + '\n')
        f.close()


def enterUserPW():
    # 创建账号密码文件，以后都不用重复输入
    try:
        with open("loginData.txt", mode='r', encoding='utf-8') as f:
            # 去掉换行符
            user = f.readline().strip()
            pw = f.readline().strip()
            f.close()
    except FileNotFoundError:
        print("Welcome to AUTO DO THE F***ING DAILY JOB, copyright belongs to S.H.")
        with open("loginData.txt", mode='w', encoding='utf-8') as f:
            user = input('Please Enter Your Username: ')
            pw = input('Then Please Enter Your Password: ')
            f.write(user + '\n')
            f.write(pw + '\n')
            f.close()

    return user, pw


date_list = {
    '1': '周一',
    '2': '周二',
    '3': '周三',
    '4': '周四',
    '5': '周五',
    '6': '周六',
    '7': '周日',
}

time_list = {
    '1': '11:30-12:30',
    '2': '12:30-13:30',
    '3': '18:00-19:00',
    '4': '19:00-20:00',
    '5': '20:00-21:00',
}


def enterOrderList():
    # 记录下要预约什么时间的场馆，以后都不用重复输入
    try:
        with open("orderList.json", mode='r', encoding='utf-8') as f:
            # 去掉换行符
            order_list = json.load(f)
            f.close()
    except FileNotFoundError:
        print("Welcome to AUTO DO THE F***ING DAILY JOB, copyright belongs to H.Y.")
        order_list = []
        while True:
            date, time = 0, 0
            print('你想预约星期几的场馆？')
            for i in range(1, len(date_list)+1):  # 输出日期列表
                print(i, ")", date_list[str(i)])
            while True:
                date = input('请输入数字：')
                date = str(date)
                if date in date_list:
                    date = int(date)
                    break
                else:
                    print('错误')
            print('你想预约哪个时间段的场馆？')
            for i in range(1, len(time_list)+1):  # 输出日期列表
                print(i, ")", time_list[str(i)])
            while True:
                time = input('请输入数字：')
                time = str(time)
                if time in time_list:
                    time = int(time)
                    break
                else:
                    print('错误')
            order_list.append([date, time])
            print('已添加计划：预约%s %s的场馆' %
                  (date_list[str(date)], time_list[str(time)]))
            con = input("还需要添加其他时间吗？y/N")
            if con != 'y' and con != 'Y':
                break
        with open("orderList.json", mode='w', encoding='utf-8') as f:
            json.dump(order_list, f)
            f.close()

    print('预约如下时间的场馆')
    for order in order_list:
        date, time = order
        print('预约%s %s的场馆' % (date_list[str(date)], time_list[str(time)]))

    return order_list


def login(user, pw, browser):
    username = browser.find_element_by_id('username')
    password = browser.find_element_by_id('password')
    username.clear()
    username.click()
    password.clear()
    password.click()
    username.send_keys(user)
    password.send_keys(pw)

    # 点击登录
    login_button = browser.find_element_by_class_name('auth_login_btn')
    login_button.submit()


lock = threading.Lock()


def make_order(url):
    browser = webdriver.Edge(executable_path='./msedgedriver.exe')
    print("------------------浏览器已启动----------------------")
    browser.get(url)
    time.sleep(3)
    login(user, pw, browser)
    time.sleep(3)
    dictCookies = browser.get_cookies()
    s = requests.Session()
    c = [s.cookies.set(c['name'], c['value']) for c in dictCookies]
    lock.acquire()
    response = s.get(
        'http://yuyue.seu.edu.cn:80/eduplus/control/validateimage')
    code = getResutlFromBuffer(response.content)
    validateCode = browser.find_element_by_id('validateCode')
    validateCode.clear()
    validateCode.click()
    validateCode.send_keys(str(code))
    browser.execute_script("submit()")
    time.sleep(2)
    lock.release()
    time.sleep(1)
    browser.get_screenshot_as_file(
        ".\\screenshots\\"+str(datetime.datetime.now())+'.png')
    browser.close()
    print("------------------浏览器已关闭----------------------")


def make_orders(order_list):
    thread_list = []
    for order in order_list:
        date, t = str(order[0]), str(order[1])
        print("预约一个%s %s的场馆" % (date_list[date], time_list[t]))
        today = datetime.date.today()
        for i in range(0, 3):
            day = today + datetime.timedelta(days=i)
            weekday = str(day.weekday()+1)
            if weekday == date:
                str_day = day.strftime('%Y-%m-%d')
                str_weekday = date_list[weekday]
                str_time = time_list[t]
                print("%s是%s, 可以预约" % (str_day, str_weekday))
                thread_list.append(
                    threading.Thread(target=make_order,
                                     args=(url % (str_day, str_time),)))
                break
    for t in thread_list:
        t.start()
        print('启动线程')
    for t in thread_list:
        t.join()


if __name__ == "__main__":
    user, pw = enterUserPW()
    order_list = enterOrderList()
    make_orders(order_list)
