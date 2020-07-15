"""
Эта программа автоматически голосует на протале Активный Гражданин.
"""
from json import load
from re import findall
from time import sleep
from os import getcwd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class VotingPrepare:
    """
    Класс логинится на сайте ag.mos.ru и
    подготовливает для бота стартовую страницу для голосования.
    Кратко: зарегался --> зашел на сайт -->
    --> нажал на кнопку доступных голосований --> вернул их количество.
    """

    def __init__(self, driver):
        """ Конструктор класса с инициализацией вебдрайвера """
        self.driver = driver

    def login(self, username, password):
        """ Логинится на сайте ag.mos.ru """
        driver = self.driver
        driver.get("https://ag.mos.ru/home")
        driver.maximize_window()

        enter_button = ".//ag-auth-actions/button[1]"
        driver.find_element_by_xpath(enter_button).click()
        sleep(1)

        mosru_buton = ".//div[@class='form-field']/button"
        driver.find_element_by_xpath(mosru_buton).click()
        sleep(1)

        login_path = "//*[@id='login']"
        driver.find_element_by_xpath(login_path).send_keys(username)
        sleep(1)

        password_path = "//*[@id='password']"
        driver.find_element_by_xpath(password_path).send_keys(password)
        sleep(1)

        enter_button = "//*[@id='bind']"
        driver.find_element_by_xpath(enter_button).click()
        sleep(3)

    def available_votings_click(self):
        """ Нажимает на кнопку доступных голосований и возвращает их количество """
        available_votings_button = "//*[@class='available-polls-button ng-star-inserted']"
        votings_count = findall(
            r"(\d+)", self.driver.find_element_by_xpath(available_votings_button).text)
        self.driver.find_element_by_xpath(available_votings_button).click()
        sleep(1)
        return int(votings_count[0])


class TypesOfquestions:
    """
    Класс, содержащий алгоритмы голосования для каждого типа, а именно:
    - Круг (1 вариант ответа)
    - Несколько вопросов типа Круг (один вариант ответа в каждом вопросе)
    - Квадрат (несколько варинтов ответа)
    - Несколько вопросов типа Квадрат (несколько вариантов ответа в каждом вопросе)
    - тип Викторина (всегда выбирает вариант - Нет, не хочу участвовать) #TODO: не реализовано
    """

    def __init__(self, driver):
        """
        Конструктор класса с инициализацией вебдрайвера и счетчиком номера вопроса.
        Голосование начинается с первого вопроса и дальше, если существует новый, счетчик
        увиличивается на 1 и выбирается следующий вопрос.
        """
        self.driver = driver
        self.question_number = 1  # счетчик номера вопроса

    def circle_and_square_type(self, question_type):
        """ Работа с типом вопросов Круг """
        sleep(2)
        # если вариант ответа юзер должен ввести сам, то выбирается второй,
        # иначе остается выбран первый
        if self.check_variant(f"//section[@class='questions-container']/ \
                                ag-poll-question[{self.question_number}]/div/ \
                                ag-variant/section/div/{question_type}"):
            self.driver.find_element_by_xpath(f"//section[@class='questions-container']/ \
                                                ag-poll-question[{self.question_number}]/div/ \
                                                ag-variant[2]/section/div/{question_type}").click()
            sleep(2)

        if self.check_next_question():
            # если существует следующий вопрос, то кликает на него
            sleep(1)
            self.click_next_question()
            sleep(1)
            self.question_number += 1  # увеличение счетчика номера вопроса
            self.type_of_question(
                ".//ag-poll-question[@class='question ng-star-inserted']/div")
        sleep(1)

    def victorina(self):
        """ Работа с типов вопросов Викторина """
        pass

    def type_of_question(self, question_type_path):
        """ определяет какой тип вопроса """
        content = self.driver.find_element_by_xpath(
            question_type_path).get_attribute("innerHTML")
        if findall('app-radio-button', content):
            self.circle_and_square_type('app-radio-button')
        elif findall('checkbox', content):
            self.circle_and_square_type('app-checkbox')
        else:
            self.victorina()

    def check_variant(self, variant_path):
        """ Проверяет является ли вариант "Своим ответом" """
        var = r'<div _ngcontent-serverapp-c14="" class="modal-content">'

        # кликаем на вариант
        self.driver.find_element_by_xpath(variant_path).click()

        # проверяем не выскочило ли поле для ввода своего варианта
        content = self.driver.find_element_by_xpath(
            "/html/body").get_attribute("innerHTML")

        var_list = findall(var, content)
        if var_list:
            # если поля для ввода есть, то закрываем его
            close_button = ".//button[@class='modal-window__close-button ng-star-inserted']"
            self.driver.find_element_by_xpath(close_button).click()
            return True
        return False

    def check_next_question(self):
        """ Проверяет наличие следующего вопроса для каждого типа """
        content = self.driver.find_element_by_xpath(
            "//section[@class='questions-container']").get_attribute("innerHTML")
        if findall('question', content) and findall('collapsed', content) and findall('ng-star-inserted', content):
            return True
        return False

    def click_next_question(self):
        """ Кликает на следующий вопрос (для всех типов) """
        sleep(1)
        self.driver.find_element_by_xpath(
            "//svg-icon[@class='icon-arrow ng-star-inserted']").click()
        sleep(2)


class Bot:
    """ Класс, работающий с браузером """

    def __init__(self):
        """ Конструктор класса с инициализацией вебдрайвера """
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        # работа браузера в невидимом режиме
        self.driver = webdriver.Chrome(executable_path=getcwd() + "\\chromedriver.exe",
                                       chrome_options=chrome_options)

    def close(self):
        """ Закрывает браузер """
        self.driver.close()

    def vote(self):
        """ Голосование в разных типах вопросов """
        driver = self.driver

        # подготовка к голосованию
        prepare = VotingPrepare(self.driver)
        with open("data.json", "r") as read_file:
            data = load(read_file)
        prepare.login(data["login"], data["password"])
        voting_count = prepare.available_votings_click()

        for _ in range(voting_count):
            sleep(1)
            # выбирает первое голосование
            vote_button = "//*[@class='ng-star-inserted']/article/div[3]/div"
            driver.find_element_by_xpath(vote_button).click()
            sleep(1)

            # определение типа вопроса и выбор алгоритма голосования
            algorithm = TypesOfquestions(driver)
            algorithm.type_of_question(
                ".//ag-poll-question[@class='question question--active ng-star-inserted']/div")

            submit_button = "//button[@class='submit-button button button--green']"
            driver.find_element_by_xpath(submit_button).click()
            sleep(1)

            no_button = "//button[@class='button button--fill button--muted']"
            driver.find_element_by_xpath(no_button).click()
            sleep(1)

            # возвращение к открытым голосованиям
            driver.get("https://ag.mos.ru/poll?filters=active")
            sleep(1)

    def mini_vote(self):
        """ Оценивает городские новинки """
        driver = self.driver
        driver.get("https://ag.mos.ru/novelties?filters=active")

        # количесвто доступных оценок
        content = driver.find_element_by_xpath(
            "//ag-cards-grid").get_attribute("innerHTML")
        count_assessments = findall("<ag-novelty-card", content)

        for _ in count_assessments:
            button = "//div[@class='footer ng-star-inserted']/div"
            driver.find_element_by_xpath(button).click()
            sleep(3)

            raiting = "//ag-rating/label[3]"
            driver.find_element_by_xpath(raiting).click()
            sleep(3)

            rate_button = "//button[@class='form__submit button button--attention button--fill']"
            driver.find_element_by_xpath(rate_button).click()
            sleep(3)

            no_button = "//button[@class='button button--fill button--muted']"
            driver.find_element_by_xpath(no_button).click()
            sleep(1)

            driver.get("https://ag.mos.ru/novelties?filters=active")
            sleep(1)


BOT = Bot()
BOT.vote()
BOT.mini_vote()
BOT.close()
