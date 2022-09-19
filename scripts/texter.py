import smtplib
import threading
from email.mime.text import MIMEText

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType
import requests
from time import sleep
import time
import logging
import json
from filelock import Timeout, FileLock
from apscheduler.schedulers.background import BackgroundScheduler
from concurrent.futures import ThreadPoolExecutor
import sys

sys.stdout = open('texter.log', 'w')

GATEWAYS_FILE_PATH = "gateways.json"
PLAYER_DATA_FILE_PATH = "player_data.json"
PLAYER_DATA_LOCK_FILE_PATH = "player_data.json.lock"


class Texter:
    def __init__(self):

        self.sender_credentials = ('tim@gpstats.dev', 'kDxs EWrm E8LC')
        with open(GATEWAYS_FILE_PATH) as gateways_file:
            self.gateways = json.load(gateways_file)

        # Thread lock for async-updated data
        self.player_data_lock = threading.Lock()
        self.active_games_lock = threading.Lock()
        self.game_state_lock = threading.Lock()

        # File lock because rest endpoint updates this file also
        player_data_file_lock = FileLock(PLAYER_DATA_LOCK_FILE_PATH)
        with player_data_file_lock:
            with open(PLAYER_DATA_FILE_PATH) as player_data_file:
                self.player_data = json.load(player_data_file)

        # no files for simplicity, will just text again if server crashes and gets restarted (not automatic)
        self.active_games = set()
        self.game_state = dict()

        # install webdriver on init
        self.op = webdriver.ChromeOptions()
        self.op.add_argument('--headless')
        self.op.add_argument('--no-sandbox')
        self.op.add_argument('--disable-dev-shm-usage')
        self.op.add_argument("--window-size=1920,1080")
        self.op.add_argument("--start-maximized")
        self.op.add_argument("--disable-gpu")
        self.op.add_argument('--disable-extensions')
        self.driver = webdriver.Chrome(ChromeDriverManager("103.0.5060.134", chrome_type=ChromeType.CHROMIUM).install(),
                                       options=self.op)

        # Thread pool for texting (slow)
        self.updating_executor = ThreadPoolExecutor(max_workers=20)
        self.texting_executor = ThreadPoolExecutor(max_workers=20)

    def __del__(self):
        self.driver.close()

    def update_player_data(self):
        player_data_file_lock = FileLock(PLAYER_DATA_LOCK_FILE_PATH)
        with player_data_file_lock:
            with open(PLAYER_DATA_FILE_PATH) as player_data_file:
                self.player_data_lock.acquire()
                try:
                    self.player_data = json.load(player_data_file)
                    print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + " : updated player data")
                finally:
                    self.player_data_lock.release()

    def update_active_games(self):
        url_games = 'https://www.boardgamers.space/boardgame/gaia-project/games'
        self.driver.get(url=url_games)
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + " : updateing active games")

        sleep(.5)
        while self.driver.execute_script("return document.readyState") != "complete":
            sleep(.5)

        num_games_found = int(self.driver.find_elements_by_class_name("card-title")[1].text.split('(')[1].split(')')[0])

        # link to click for next page
        next_button = self.driver.find_elements_by_class_name("page-link")[-2]

        # list of names items
        active_games_list = self.driver.find_elements_by_class_name("game-list")[-1]
        game_names = active_games_list.find_elements_by_class_name("game-name")

        self.active_games_lock.acquire()
        try:
            for name in game_names:
                n = name.text
                if n not in self.active_games:
                    self.active_games.add(n)
        finally:
            self.active_games_lock.release()

        for i in range(num_games_found // 10):
            try:
                next_button.click()
                sleep(.5)
            except:
                continue

            # wait for JS to load -> elements are same, only text and class are updated
            while self.driver.execute_script("return document.readyState") != "complete":
                sleep(.5)

            next_button = self.driver.find_elements_by_class_name("page-link")[-2]

            active_games_list = self.driver.find_elements_by_class_name("game-list")[-1]
            game_names = active_games_list.find_elements_by_class_name("game-name")

            self.active_games_lock.acquire()
            try:
                for name in game_names:
                    n = name.text
                    if n not in self.active_games:
                        self.active_games.add(n)
            finally:
                self.active_games_lock.release()

    def text(self, country, provider, number, username, game):
        sender_email, email_password = self.sender_credentials
        subject = "registered for gpstats texts"
        message = "You are registered to receive turn reminder texts for your " + username + " bgs account!"
        link_found = False
        link = ''
        for g in self.gateways:
            if g.get("country").upper() == country.upper() and g.get("provider").upper() == provider.upper():
                link_found = True
                link = g.get("link")

        link_split = link.split("#")
        receiver_email = link_split[0] + str(number) + link_split[-1]

        games_link = "https://www.boardgamers.space/game/" + game

        body_1 = f"Your move in {game}."
        body_2 = f"Goto: {games_link}"

        msg1 = MIMEText(body_1)
        msg1['Subject'] = ""
        msg1['From'] = sender_email
        msg1['To'] = receiver_email
        msg2 = MIMEText(body_2)
        msg2['Subject'] = ""
        msg2['From'] = sender_email
        msg2['To'] = receiver_email

        server = smtplib.SMTP_SSL('smtppro.zoho.com', 465)
        server.login(sender_email, email_password)
        server.sendmail(sender_email, [receiver_email], msg1.as_string())
        server.sendmail(sender_email, [receiver_email], msg2.as_string())
        server.quit()

        return link_found

    def check_games_and_update(self):
        base_url = "https://www.boardgamers.space/api/game/"

        self.active_games_lock.acquire()
        try:
            games = self.active_games.copy()
        finally:
            self.active_games_lock.release()

        for game_name in games:
            self.updating_executor.submit(self.check_game_and_update, game_name)

    def check_game_and_update(self, game_name):
        base_url = "https://www.boardgamers.space/api/game/"

        with requests.Session() as session:
            with session.get(base_url + game_name) as response:
                if response.status_code != 200:
                    return

                game_tree = response.json()

                if game_tree['status'] != "active":
                    # remove from active games
                    self.active_games_lock.acquire()
                    try:
                        self.active_games.remove(game_name)
                    finally:
                        self.active_games_lock.release()

                    # remove from game state
                    self.game_state_lock.acquire()
                    try:
                        self.game_state.pop(game_name)
                    finally:
                        self.game_state_lock.release()
                else:
                    if game_name in self.game_state:
                        cur_player_id = self.game_state.get(game_name)
                        moving_player_id = game_tree['currentPlayers'][0]['_id']
                        if moving_player_id == cur_player_id:
                            return
                        else:
                            self.game_state_lock.acquire()
                            try:
                                self.game_state[game_name] = moving_player_id
                            finally:
                                self.game_state_lock.release()

                            for player in game_tree['players']:
                                if player['_id'] == moving_player_id:
                                    username = player['name']
                                    if username in self.player_data:
                                        user_data = self.player_data.get(username)
                                        print(time.strftime("%Y-%m-%d %H:%M:%S",
                                                            time.gmtime()) + " : sending text : " + username + " " + user_data.get(
                                            'country') + " " + user_data.get('provider') + " " + user_data.get(
                                            'number'))
                                        self.texting_executor.submit(self.text, user_data.get('country'),
                                                                     user_data.get('provider'), user_data.get('number'),
                                                                     username, game_name)
                    else:
                        moving_player_id = game_tree['currentPlayers'][0]['_id']

                        self.game_state_lock.acquire()
                        try:
                            self.game_state[game_name] = moving_player_id
                        finally:
                            self.game_state_lock.release()

                        for player in game_tree['players']:
                            if player['_id'] == moving_player_id:
                                username = player['name']
                                if username in self.player_data:
                                    user_data = self.player_data.get(username)
                                    print(time.strftime("%Y-%m-%d %H:%M:%S",
                                                        time.gmtime()) + " : sending text : " + username + " " + user_data.get(
                                        'country') + " " + user_data.get('provider') + " " + user_data.get('number'))
                                    self.texting_executor.submit(self.text, user_data.get('country'),
                                                                 user_data.get('provider'), user_data.get('number'),
                                                                 username, game_name)


if __name__ == "__main__":
    texter = Texter()
    texter.update_player_data()
    texter.update_active_games()
    texter.check_games_and_update()

    sched = BackgroundScheduler(daemon=False)
    sched.add_job(texter.update_player_data, 'interval', seconds=10)
    sched.add_job(texter.update_active_games, 'interval', seconds=60)
    sched.add_job(texter.check_games_and_update, 'interval', seconds=30)
    sched.start()

    # texter.update_player_data()
    # texter.update_active_games()
    # texter.check_games_and_update()
    # texter.text('United States', 'T-Mobile', '4022171278', 'augury', 'Euclidean-dynamo-6514')
