import time

from SEURobot import SEURobot
from login_config import username, password
seu_bot = SEURobot(username, password)

if __name__ == "__main__":
    browser = seu_bot.open(
        "http://yuyue.seu.edu.cn/eduplus/order/fetchMyOrders.do?sclId=1")
    browser.implicitly_wait(10)
    time.sleep(10)
    browser.close()
