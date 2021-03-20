import time
import requests


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


def login(browser):
    user, pw = enterUserPW()
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


def get_session_for_requests(browser):
    dictCookies = browser.get_cookies()
    s = requests.Session()
    c = [s.cookies.set(c['name'], c['value']) for c in dictCookies]
    return s
