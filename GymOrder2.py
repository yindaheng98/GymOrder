from GymOrder import *
from SEURobot import SEURobot
from time_config import next_weekday,time_list_weekend
from login_config import username2, password2

time_config = [
    next_weekday('周日') + " " + time_list_weekend[6],
]

def get_seubot():
    return SEURobot(username2, password2)

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