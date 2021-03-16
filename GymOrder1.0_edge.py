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

# 加启动配置 禁用日志log
# ie capabilities
# capabilities = DesiredCapabilities.INTERNETEXPLORER
# capabilities.pop("platform", None)
# capabilities.pop("version", None)


url = "http://ehall.seu.edu.cn/appShow?appId=4815356910091974"
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
        date,time = order
        print('预约%s %s的场馆' % (date_list[str(date)], time_list[str(time)]))

    return order_list


def login(user, pw, browser):
    browser.get(url)
    browser.implicitly_wait(10)

    # 填写用户名密码
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

# 检查是否无text按钮


def check(text, browser):
    buttons = browser.find_elements_by_tag_name('button')
    for button in buttons:
        if button.get_attribute("textContent").find(text) >= 0:
            return True
    return False


def main(browser):
    pass


if __name__ == "__main__":
    user, pw = enterUserPW()
    order_list = enterOrderList()
    localtime = time.localtime(time.time())
    set_minite = localtime.tm_min  # 首次登陆的分钟时刻，代表以后每次在此分钟时刻打卡
    set_hour = localtime.tm_hour  # 首次登陆的时钟时刻，代表以后每次在此时钟时刻打卡

    if set_hour > 9:
        set_hour = 7  # 如果首次登录超过上午10点，则以后默认在7点钟打卡
        first_time = True

    while True:
        try:
            # 登录打卡一次试一试
            browser = webdriver.Edge(executable_path='./msedgedriver.exe')
            print("------------------浏览器已启动----------------------")
            login(user, pw, browser)
            browser.implicitly_wait(10)
            time.sleep(10)

            # 确认是否打卡成功
            # 的确无新增按钮
            dailyDone = not check("新增", browser)
            if dailyDone is True and check("退出", browser) is True:  # 今日已完成打卡
                sleep_time = (set_hour+24-time.localtime(time.time()).tm_hour) * \
                    3600 + (set_minite-time.localtime(time.time()).tm_min)*60
                writeLog("下次打卡时间：明天" + str(set_hour) + ':' +
                         str(set_minite) + "，" + "即" + str(sleep_time) + 's后')
                browser.close()
                print("------------------浏览器已关闭----------------------")
                time.sleep(sleep_time)
            elif dailyDone is False:  # 今日未完成打卡
                # 点击报平安
                buttons = browser.find_elements_by_css_selector('button')
                for button in buttons:
                    if button.get_attribute("textContent").find("新增") >= 0:
                        button.click()
                        browser.implicitly_wait(10)

                        # 输入温度37°
                        inputfileds = browser.find_elements_by_tag_name(
                            'input')
                        for i in inputfileds:
                            if i.get_attribute("placeholder").find("请输入当天晨检体温") >= 0:
                                i.click()
                                i.send_keys(str(random.randint(365, 370)/10.0))

                                # 确认并提交
                                buttons = browser.find_elements_by_tag_name(
                                    'button')
                                for button in buttons:
                                    if button.get_attribute("textContent").find("确认并提交") >= 0:
                                        button.click()
                                        buttons = browser.find_elements_by_tag_name(
                                            'button')
                                        button = buttons[-1]
                                        # 提交
                                        if button.get_attribute("textContent").find("确定") >= 0:
                                            button.click()
                                            dailyDone = True  # 标记已完成打卡
                                            writeLog("打卡成功")
                                        break
                                break
                        break
                browser.close()
                print("------------------浏览器已关闭----------------------")
                time.sleep(10)  # 昏睡10s 为了防止网络故障未打上卡
            else:
                browser.close()
                print("------------------网站出现故障----------------------")
                print("------------------浏览器已关闭----------------------")
                time.sleep(300)  # 昏睡5min 为了防止网络故障未打上卡
        except Exception as r:
            print("未知错误 %s" % (r))
