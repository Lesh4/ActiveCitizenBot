"""
This program votes in "Active citizen"
"""
from json import load
from re import findall
from time import sleep
from os import getcwd
from selenium import webdriver


class VotingPrepare:
    """ This class logins in ag.mos.ru
    and gives to the Bot start page with
    available votings"""

    def __init__(self, driver):
        """Class constructor with webdriver initialization"""
        self.driver = driver

    def login(self, username, password):
        """ Login in ag.mos.ru """
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
        """ Finds button with count of available votings"""
        available_votings_button = "//*[@class='available-polls-button ng-star-inserted']"
        votings_count = findall(
            r"(\d+)", self.driver.find_element_by_xpath(available_votings_button).text)
        self.driver.find_element_by_xpath(available_votings_button).click()
        sleep(1)
        return int(votings_count[0])


class TypesOfquestions:
    """ Has different algorithms for each type of question.
    Types of questions:
    - Circle (1 answer variant)
    - Some count of Circle question (a lot of questions with 1 answer variant)
    - Square (several answer variants/one or more variant)
    - Some count of Square question (a lot of questions with several answer variants)
    - Victorina type (always choose 'Нет, не хочу участвовать')
    """

    def __init__(self, driver):
        self.driver = driver
        self.num = 1  # counters of number of guestions

    def circle(self):
        """ Works with type Circle"""
        sleep(2)
        if self.check_variant(variant_path := f"//section[@class='questions-container']/ \
                                                ag-poll-question[{self.num}]/div/ \
                                                ag-variant/section/div/app-radio-button"):
            self.driver.find_element_by_xpath(f"//section[@class='questions-container']/ \
                                                ag-poll-question[{self.num}]/div/ \
                                                ag-variant[2]/section/div/app-radio-button").click()
            sleep(2)
        else:
            self.driver.find_element_by_xpath(variant_path).click()
            sleep(2)

        if self.check_next_question():
            # if 'next_question' is, then click its
            sleep(1)
            self.click_next_question()
            sleep(1)
            self.num += 1  # update counter of number of guestions
            self.type_of_question(
                ".//ag-poll-question[@class='question ng-star-inserted']/div")
        sleep(1)

    def square(self):
        """ Works with type Square"""
        sleep(1)
        if self.check_variant(variant_path := f"//section[@class='questions-container']/ \
                                                ag-poll-question[{self.num}]/div/ \
                                                ag-variant/section/div/app-checkbox"):
            # if variant is 'свой вариант', then choose the second
            self.driver.find_element_by_xpath(f"//section[@class='questions-container']/ \
                                                ag-poll-question[{self.num}]/div/ \
                                                ag-variant[2]/section/div/app-checkbox").click()
            sleep(2)
        else:
            # choose the first variant
            self.driver.find_element_by_xpath(variant_path).click()
            sleep(2)

        if self.check_next_question():
            # if 'next_question' is, then click its
            sleep(1)
            self.click_next_question()
            sleep(1)
            self.num += 1  # update counter of number of guestions
            self.type_of_question(
                ".//ag-poll-question[@class='question ng-star-inserted']/div")
        sleep(1)

    def victorina(self):
        """ Works with type Victorina"""
        pass

    def type_of_question(self, path):
        """ Defines what type of question is """
        question_type_path = path
        content = self.driver.find_element_by_xpath(
            question_type_path).get_attribute("innerHTML")
        if findall('app-radio-button', content):
            self.circle()
        elif findall('checkbox', content):
            self.square()
        else:
            self.victorina()

    def check_variant(self, variant_path):
        """ Checks an option according to the principle: is there 'Свой вариант'"""
        var = r"Свой вариант ответа"
        content = self.driver.find_element_by_xpath(
            variant_path).get_attribute("innerHTML")
        var_list = findall(var, content)
        if var_list:
            return True
        return False

    def check_next_question(self):
        """ Checks existence of other questions (for 1 and 3 tupes)"""
        content = self.driver.find_element_by_xpath(
            "//section[@class='questions-container']").get_attribute("innerHTML")
        if findall('question question--collapsed collapsed ng-star-inserted', content):
            return True
        elif findall('question collapsed ng-star-inserted \
                      question--active question--collapsed', content):
            return True
        elif findall('question question--active question-- \
                      collapsed collapsed ng-star-inserted', content):
            return True
        return False

    def click_next_question(self):
        """ Clicks next question (for 1 and 3 tupes)"""
        sleep(1)
        self.driver.find_element_by_xpath(
            "//svg-icon[@class='icon-arrow ng-star-inserted']").click()
        sleep(2)


class Bot:
    """ This class is for work with browser """

    def __init__(self):
        """Class constructor with webdriver initialization"""
        self.driver = webdriver.Chrome(getcwd() + "\\chromedriver.exe")

    def vote(self):
        """ Votes in different types of questions"""
        driver = self.driver

        # prepare for voting
        prepare = VotingPrepare(self.driver)
        with open("data.json", "r") as read_file:
            data = load(read_file)
        prepare.login(data["login"], data["password"])
        voting_count = prepare.available_votings_click()

        for _ in range(voting_count):
            sleep(1)
            # choose the first voting
            vote_button = "//*[@class='ng-star-inserted']/article/div[3]/div"
            driver.find_element_by_xpath(vote_button).click()
            sleep(1)

            # determining the type of question and choose the algorithms
            algorithm = TypesOfquestions(driver)
            algorithm.type_of_question(
                ".//ag-poll-question[@class='question question--active ng-star-inserted']/div")

            submit_button = "//button[@class='submit-button button button--green']"
            driver.find_element_by_xpath(submit_button).click()
            sleep(1)

            no_button = "//button[@class='button button--fill button--muted']"
            driver.find_element_by_xpath(no_button).click()
            sleep(1)

            # return to votings
            driver.get("https://ag.mos.ru/poll?filters=active")
            sleep(1)

    def mini_vote(self):
        """ Rates noveltys"""
        driver = self.driver
        driver.get("https://ag.mos.ru/novelties?filters=active")

        # count of open 'городские новинки'
        content = driver.find_element_by_xpath(
            "//ag-cards-grid").get_attribute("innerHTML")
        count_assessments = findall("ag-novelty-card", content)

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
