from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas
import json
import requests
from time import sleep
from tqdm.notebook import tqdm, trange


def update_names():
    op = webdriver.ChromeOptions()
    op.add_argument('headless')
    driver = webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install(), options=op)

    url_games = 'https://www.boardgamers.space/boardgame/gaia-project/games'

    games_set = set()

    with open("game_names.txt", "r") as names_file:
        lines = names_file.readlines()
        for line in lines:
            games_set.add(line)

    names_file.close()

    driver.get(url=url_games)
    finished_button = driver.find_element_by_partial_link_text("Finished")
    finished_button.click()

    # link to click for next page
    next_button = driver.find_elements_by_class_name("page-link")[-2]
    # parent <li> can be disabled if last page
    next_item = driver.find_elements_by_class_name("page-item")[-2]
    # list of disabled items
    disabled_items = driver.find_elements_by_class_name("disabled")

    # list of names items
    game_names = driver.find_elements_by_class_name("game-name")

    with open("game_names.txt", "a") as names_file:

        for name in game_names:
            n = name.text
            if n not in games_set:
                names_file.write(n + '\n')

        while next_item not in disabled_items:
            try:
                next_button.click()
                sleep(.1)

                # wait for JS to load -> elements are same, only text and class are updated
                while driver.execute_script("return document.readyState") != "complete":
                    sleep(.05)

                next_button = driver.find_elements_by_class_name("page-link")[-2]
                next_item = driver.find_elements_by_class_name("page-item")[-2]
                disabled_items = driver.find_elements_by_class_name("disabled")

                game_names = driver.find_elements_by_class_name("game-name")

                for name in game_names:
                    n = name.text
                    if n not in games_set:
                        names_file.write(n + '\n')
            except:
                break

    names_file.close()