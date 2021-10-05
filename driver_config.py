from selenium import webdriver


def webdriver_init():
    return webdriver.Edge(executable_path='./msedgedriver.exe')