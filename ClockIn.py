import datetime
import random
import time
#每日打卡

from selenium.webdriver.support.wait import WebDriverWait  # 等待页面加载某些元素

from SEURobot import SEURobotFromFile
from logger import logger

logging = logger

class SEUClockIn:
    def __init__(self, login_data_path = "loginData.txt"):
        self.url = "http://ehall.seu.edu.cn/qljfwapp2/sys/lwReportEpidemicSeu/*default/index.do"
        self.login_data_path = login_data_path

    @staticmethod
    def _check(browser, text):
        buttons = browser.find_elements_by_tag_name('button')
        for button in buttons:
            if button.get_attribute("textContent").find(text) >= 0:
                return button
        return False

    def _clock_in(self, browser):
        button = self._check(browser, "新增")
        if button is False:  # 今日已完成打卡
            return

        button.click()
        browser.implicitly_wait(10)

        # 输入温度37°
        for i in browser.find_elements_by_tag_name('input'):
            if i.get_attribute("placeholder").find("请输入当天晨检体温") >= 0:
                i.click()
                i.send_keys(str(random.randint(365, 370) / 10.0))

                # 确认并提交
                buttons = browser.find_elements_by_tag_name('button')
                for button in buttons:
                    if button.get_attribute("textContent").find("确认并提交") >= 0:
                        button.click()
                        buttons = browser.find_elements_by_tag_name('button')
                        button = buttons[-1]
                        # 提交
                        if button.get_attribute("textContent").find("确定") >= 0:
                            button.click()
                        break
                break

    def run(self):
        for i in range(10):
            logging.info("第%d次尝试"%i)
            try:
                bot = SEURobotFromFile(self.login_data_path)
                browser = bot.open(self.url)
                WebDriverWait(browser, 10).until(lambda x: self._check(x, '退出'))
                browser.implicitly_wait(random.randint(0, 60))
                self._clock_in(browser)
                browser.get_screenshot_as_file(
                    "screenshots/" + datetime.datetime.now().strftime("%Y%m%d-%H.%M.%S") + '.png')
                browser.close()
                browser = bot.open(self.url)
                WebDriverWait(browser, 10).until(lambda x: self._check(x, '退出'))
                if self._check(browser, "新增") is False:
                    logging.info("打卡已完成")
                    browser.close()
                    break
                else:
                    browser.close()
            except Exception as e:
                logging.error("未知错误 %s" % e)


if __name__ == "__main__":
    clock = SEUClockIn()
    clock.run()
    while True:
        time.sleep(1)
        now = datetime.datetime.now()
        if now.hour >= 8 and  now.hour < 9 and now.minute < 30:
            logging.info("现在是%s, 可以签到了" % datetime.datetime.now())
            clock.run()
        else:
            print("现在是%s, 没到时间，等一会" % datetime.datetime.now())
            if now.minute % 10 == 0 and now.second % 10 <= 1:
                logging.info("现在是%s, 没到时间，脚本在线" % datetime.datetime.now())
