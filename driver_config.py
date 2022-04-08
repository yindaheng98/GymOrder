from selenium import webdriver

chrome_options = webdriver.ChromeOptions()
chrome_options.set_capability('browserless.token', 'YOUR-API-TOKEN')
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--headless")


def webdriver_init():
    return webdriver.Remote(
        command_executor='http://localhost:3000/webdriver',
        desired_capabilities=chrome_options.to_capabilities()
    )  # webdriver.Edge(executable_path='./msedgedriver.exe')

def webdriver_init_local():
    return webdriver.Edge(executable_path='./msedgedriver.exe')