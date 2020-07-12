"""Проверка подлинности логина или пароля на Активном Гражданине"""
from requests import get
from time import sleep
from json import load, dump
from os import getcwd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

CHROME_OPTIONS = Options()
CHROME_OPTIONS.add_argument("--headless")
CHROME_OPTIONS.add_argument("--window-size=1920,1080")

DRIVER = webdriver.Chrome(executable_path=getcwd() + "\\chromedriver.exe",
                               chrome_options=CHROME_OPTIONS)


def profile_picture_download():
    """ Скачивание аватраки пользователя с сайта """
    DRIVER.get("https://ag.mos.ru/profile")
    sleep(1)

    default_url = 'https://service.ag.mos.ru/static/default_avatar.png'
    image_path = ".//ag-avatar[@class='avatar']"
    content = DRIVER.find_element_by_xpath(image_path).get_attribute("innerHTML")
    
    url = content.split('src="')[1].split('">')[0]
    if url != default_url:
        with open("packages/avatar.png", "wb") as write_file:
            write_file.write(get(url).content)



class AutarizationTest():
    def __init__(self, login, password):
        """ Инициализация драйвера и переход на сайт mos.ru """
        DRIVER.get("https://ag.mos.ru/home")
        DRIVER.maximize_window()

        self.login = login
        self.password = password

    def close(self):
        """ Закрытие браузера """
        DRIVER.close()

    def autarization(self):
        """ Ввод данных на сайте mos.ru """

        enter_button = ".//ag-auth-actions/button[1]"
        DRIVER.find_element_by_xpath(enter_button).click()
        sleep(1)

        mosru_buton = ".//div[@class='form-field']/button"
        DRIVER.find_element_by_xpath(mosru_buton).click()
        sleep(1)

        login_path = "//*[@id='login']"
        DRIVER.find_element_by_xpath(login_path).send_keys(self.login)
        sleep(1)

        password_path = "//*[@id='password']"
        DRIVER.find_element_by_xpath(password_path).send_keys(self.password)
        sleep(1)

        enter_button = "//*[@id='bind']"
        DRIVER.find_element_by_xpath(enter_button).click()
        sleep(3)

    def enter_check(self):
        """ Проверка подлинности пароля или логина """
        content = "//blockquote[@class='blockquote-danger']"

        try:
            # если есть блок с информацией о неверном пароле или логине, то enter_check не прошло, возвращатся False
            DRIVER.find_element_by_xpath(content).get_attribute("innerHTML")
            return False
        except NoSuchElementException as exception:
            print(exception)
            # если такого элемента нет, значит логин и пароль верны
            return True


with open("data.json", "r") as read_file:
    data = load(read_file)

autarizationTest = AutarizationTest(data["login"], data["password"])
autarizationTest.autarization()

with open("authorization_status.json", "w") as write_file:
    if autarizationTest.enter_check():
        dump({"authorization_status" : "True"}, write_file)
        profile_picture_download()
    else:
        dump({"authorization_status" : "False"}, write_file)
autarizationTest.close()