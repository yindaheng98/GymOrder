import datetime


def __next_weekday(day, weekday):  # 寻找下一个日期
    date_list = {
        '周一': 0,
        '周二': 1,
        '周三': 2,
        '周四': 3,
        '周五': 4,
        '周六': 5,
        '周日': 6,
    }
    weekday = date_list[weekday]  # 转成数字
    days_ahead = weekday - day.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    return day + datetime.timedelta(days_ahead)


def next_weekday(weekday):  # 从今天开始的下一个日期
    return __next_weekday(datetime.date.today(), weekday).strftime("%Y-%m-%d")


time_list_weekday = [  # 非节假日可选的时间
    '11:30-12:30',
    '12:30-13:30',
    '18:00-19:00',
    '19:00-20:00',
    '20:00-21:00',
]

time_list_weekend = [  # 节假日可选的时间
    '09:00-10:00',
    '10:00-11:00',
    '11:00-12:00',
    '12:00-13:00',
    '13:00-14:00',
    '14:00-15:00',
    '15:00-16:00',
    '16:00-17:00',
    '17:00-18:00',
    '18:00-19:00',
]

time_config = [
    (next_weekday('周六'), time_list_weekend[6]),
    (next_weekday('周六'), time_list_weekend[7]),
    (next_weekday('周日'), time_list_weekend[6]),
    (next_weekday('周日'), time_list_weekend[7]),
]

print(time_config)

