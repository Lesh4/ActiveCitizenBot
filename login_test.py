"""Проверка подлинности логина или пароля на Активном Гражданине"""
from time import sleep
from json import load, dump
from os import getcwd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException


class AutarizationTest():
    def __init__(self, login, password):
        """ Инициализация драйвера и переход на сайт mos.ru """
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")

        self.driver = webdriver.Chrome(executable_path=getcwd() + "\\chromedriver.exe",
                                       chrome_options=chrome_options)
        self.driver.get("https://www.mos.ru/")
        self.driver.maximize_window()
        sleep(1)

        self.login = login
        self.password = password

    def close(self):
        """ Закрытие браузера """
        self.driver.close()

    def autarization(self):
        """ Ввод данных на сайте mos.ru """
        driver = self.driver

        enter_button_path = "//*[@id='mos-header']/div[2]/div/header/div[2]/div/button"
        driver.find_element_by_xpath(enter_button_path).click()
        sleep(2)

        login_path = "//*[@id='login']"
        driver.find_element_by_xpath(login_path).send_keys(self.login)
        sleep(1)

        password_path = "//*[@id='password']"
        driver.find_element_by_xpath(password_path).send_keys(self.password)
        sleep(1)

        enter_button = "//*[@id='bind']"
        driver.find_element_by_xpath(enter_button).click()
        sleep(3)

    def enter_check(self):
        """ Проверка подлинности пароля или логина """
        driver = self.driver
        content = "//blockquote[@class='blockquote-danger']"

        try:
            # если есть блок с информацией о неверном пароле или логине, то enter_check не прошло, возвращатся False
            driver.find_element_by_xpath(content).get_attribute("innerHTML")
            return False
        except NoSuchElementException as exception:
            print(exception)
            # если такого элемента нет, значит логин и пароль верны
            return True


with open("data_test.json", "r") as read_file:
    data = load(read_file)

autarizationTest = AutarizationTest(data["login"], data["password"])
autarizationTest.autarization()

with open("autarization_status.json", "w") as write_file:
    if autarizationTest.enter_check():
        dump({"autarization_status" : "True"}, write_file)
    else:
        dump({"autarization_status" : "False"}, write_file)
autarizationTest.close()