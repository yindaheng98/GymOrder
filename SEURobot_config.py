import time

from SEURobot import SEURobot
from login_config import username, password


def get_seubot():
    return SEURobot(username, password)


if __name__ == "__main__":
    seu_bot = get_seubot()
    browser = seu_bot.open(
        "http://yuyue.seu.edu.cn/eduplus/order/fetchMyOrders.do?sclId=1")
    browser.implicitly_wait(10)
    session = seu_bot.getRequestsSession()
    print(session.get("http://yuyue.seu.edu.cn/eduplus/control/validateimage").content)
    browser.get("http://yuyue.seu.edu.cn/eduplus/control/validateimage")
    time.sleep(10)
    browser.close()
