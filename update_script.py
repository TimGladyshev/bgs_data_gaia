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
import pandas
import json
import requests
from time import sleep
from tqdm.notebook import tqdm, trange
import asyncio
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor
from timeit import default_timer
import multiprocessing
import nest_asyncio
import os
import pandas as pd
pd.set_option('display.max_rows', 200)
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 1000)
import json
import numpy
from IPython.display import display
from subprocess import check_output
import sys
import traceback
from tqdm.notebook import tqdm, trange


techs = {
        "tech1": "1q_1o",
        "tech2": "k_per_terra",
        "tech3": "4pip",
        "tech4": "7vp",
        "tech5": "1o_1pw",
        "tech6": "1k_1c",
        "tech7": "3vp_per_gaia_place",
        "tech8": "4c",
        "tech9": "4pw",
        # idk wtf this is --> "tech-ship0": "2c_per_trade"
    }

adv_techs = {
        "advtech1": "3vp_per_fed_pass",
        "advtech2": "2vp_per_tech_bump",
        "advtech3": "1qic_5c_action",
        "advtech4": "2vp_per_mine",
        "advtech5": "3vp_per_rl_pass",
        "advtech6": "1o_per_sector",
        "advtech7": "1vp_per_terra_pass",
        "advtech8": "2vp_per_gaia",
        "advtech9": "4vp_per_ts",
        "advtech10": "2vp_per_sector",
        "advtech11": "3o_action",
        "advtech12": "5vp_per_fed",
        "advtech13": "3k_action",
        "advtech14": "3vp_per_mine_place",
        "advtech15": "3vp_per_ts_place",
    }

feds = {
        "fed1": "12vp",
        "fed2": "qic",
        "fed3": "2pw",
        "fed4": "2o",
        "fed5": "6c",
        "fed6": "2k",
        "gleens": "gleens"
    }

round_scorings = {
        "score1": "2vp_per_terra",
        "score2": "2vp_per_research_bump",
        "score3": "2vp_per_mine_place",
        "score4": "5vp_per_fed_place",
        "score5": "4vp_per_ts_place",
        "score6": "4vp_per_gaia_place",
        "score7": "5vp_per_3pip_place",
        "score8": "3vp_per_ts_place",
        "score9": "3vp_per_gaia_place",
        "score10": "5vp_per_3pip_place",
    }

boosters = {

        "booster1": "1k_1o",
        "booster2": "2pwt_1o",
        "booster3": "1qic_2c",
        "booster4": "2c_terra",
        "booster5": "2pw_nav",
        "booster6": "1o_1vp_per_mine",
        "booster7": "1o_2vp_per_ts",
        "booster8": "1k_3vp_per_rl",
        "booster9": "4pw_4vp_per_3pip",
        "booster10": "4c_1vp_per_gaia",
    }

bad_buildings = {"colony",
                     "colonyShip",
                     "tradeShip",
                     "constructionShip",
                     "researchShip",
                     "scout",
                     "frigate",
                     "battleShip",
                     "customsPost",
                     "tradePost"
                     }


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

    sleep(.5)
    while driver.execute_script("return document.readyState") != "complete":
        sleep(.05)

    num_games_found = int(driver.find_element_by_class_name("card-title").text.split('(')[1].split(')')[0])

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

        for i in range((num_games_found - len(games_set)) // 10):
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
    driver.close()


def fetch(session, game_name, lock, file):
    base_url = "https://www.boardgamers.space/api/game/"
    with session.get(base_url + game_name) as response:
        data = response.json()
        if response.status_code != 200:
            return 1
        else:
            with lock:
                try:
                    file.write(json.dumps(data) + "\n")
                except Exception as err:
                    print(err)
                finally:
                    return 0
    return 0


async def get_data_asynchronous(names_set, file_lock, file):
    with ThreadPoolExecutor(max_workers=10) as executor:
        with requests.Session() as session:
            loop = asyncio.get_event_loop()

            tasks = [
                loop.run_in_executor(
                    executor,
                    fetch,
                    *(session, name, file_lock, file)
                )
                for name in names_set
            ]

            for response in await asyncio.gather(*tasks):
                pass


def fetch_jsons():
    game_names = open("game_names.txt", "r")
    names_set = set()
    for name in game_names:
        names_set.add(name)

    game_names.close()

    # clear jsons
    open('game_data_raw.txt', 'w').close()

    m = multiprocessing.Manager()
    lock = m.Lock()
    loop = asyncio.get_event_loop()
    with open("game_data_raw.txt", "a") as game_data_raw:
        future = asyncio.ensure_future(get_data_asynchronous(names_set, lock, game_data_raw))
        loop.run_until_complete(future)

        game_data_raw.close()


def wc(filename):
    return int(check_output(["wc", "-l", filename]).split()[0])


def parse_tree_builds(dat, tree, pos, faction):
    moves = tree['data']['moveHistory']
    logs = tree['data']['advancedLog']

    cur_round = 0
    built = {
        'm': 0,
        'ts': 0,
        'lab': 0,
        'ac1': 0,
        'ac2': 0,
        'PI': 0,
        'gf': 0,
    }
    for log in logs:
        if 'round' in log.keys():
            cur_round = log['round']
            if cur_round > 1:
                for key in built.keys():

                    # catch all negative amounts
                    if built[key] < 0:
                        raise ValueError(
                            'negative structure amount found : ' + key + ' ' + faction + ' ' + str(cur_round))

                    dat[pos + 'buildings_r_' + str(cur_round - 1) + '_' + key] = built[key]

        if 'move' in log.keys():
            move = moves[log['move']]
            if 'build' in move and faction in move:
                struct = move.split('build')[1].split()[0]
                if struct in built.keys():
                    built[struct] += 1

                if struct == 'ts' and 'special' not in move:
                    built['m'] -= 1
                elif struct == 'ts' and 'special' in move:
                    built['lab'] -= 1
                elif struct == 'PI' and not faction == 'ivits':
                    if faction == 'bescods':
                        built['lab'] -= 1
                    else:
                        built['ts'] -= 1
                elif struct == 'lab':
                    built['ts'] -= 1
                elif struct == 'ac1' or struct == 'ac2':
                    if faction == 'bescods':
                        built['ts'] -= 1
                    else:
                        built['lab'] -= 1

    return dat


"""
Parses non-expansion game data

ToDo: iterate through game moves to get first turn builings, and score vp disterbution
"""


def parse_tree(tree, errors_set):
    if not tree['cancelled'] and tree['status'] == 'ended':
        try:
            dat = {}
            dat['id'] = tree['_id']

            # check for expansions
            if 'expansions' in tree['game'].keys() and len(tree['game']['expansions']) > 0:
                raise ValueError('this game is with expansions: ' + ''.join(tree['game']['expansions']))
            if 'expansions' in tree['data'].keys() and tree['data']['expansions'] != 0:
                raise ValueError('this game is with expansions: ' + str(tree['data']['expansions']))

            # some jsons dont have layout. must be before the site supported that feature
            # assume standard
            if 'options' in tree['data'].keys() and 'layout' in tree['data']['options'].keys():
                dat['map_layout'] = tree['data']['options']['layout']
            else:
                dat['map_layout'] = 'standard'

            num_players = tree['options']['setup']['nbPlayers']
            dat['num_players'] = num_players
            tot_elo = 0

            # boosters in game
            found_boosters = tree['data']['tiles']['boosters']
            for i in range(10):
                booster_name = 'booster' + str(i + 1)
                if booster_name in found_boosters.keys():
                    dat[boosters[booster_name]] = True
                else:
                    dat[boosters[booster_name]] = False

            # tech locations
            found_techs = tree['data']['tiles']['techs']
            for loc in found_techs.keys():
                name = found_techs[loc]['tile']
                if name in techs:
                    dat['tech_' + loc] = techs[name]
                elif name in adv_techs:
                    dat['tech_' + loc] = adv_techs[name]
                else:
                    raise NameError('unknown tech: ' + name)
                    # dat['tech_' + loc] = name

            # scorings
            found_scorings = tree['data']['tiles']['scorings']['round']
            for i in range(len(found_scorings)):
                dat['round_' + str(i + 1) + '_scoring'] = round_scorings[found_scorings[i]]
            dat['final_scoring_1'] = tree['data']['tiles']['scorings']['final'][0]
            dat['final_scoring_2'] = tree['data']['tiles']['scorings']['final'][1]

            # player data
            for i in range(num_players):

                # position
                pos = "pos_" + str(tree['players'][i]['ranking']) + "_"

                # dropped or no
                dat[pos + 'dropped'] = tree['players'][i]['dropped']

                # elo
                elo = tree['players'][i]['elo']['initial']
                tot_elo += elo
                dat[pos + 'elo'] = elo

                # faction
                faction = tree['players'][i]['faction']
                dat[pos + 'faction'] = faction

                # score
                dat[pos + 'score'] = tree['players'][i]['score']

                # start pos
                dat[pos + 'start_pos'] = \
                [i + 1 for i in range(len(tree['data']['setup'])) if tree['data']['setup'][i] == faction][0]

                # bid
                dat[pos + 'bid'] = tree['data']['players'][i]['data']['bid']

                # feds
                feds_taken = tree['data']['players'][i]['data']['tiles']['federations']
                dat[pos + 'feds_taken'] = len(feds_taken)
                for key in feds.keys():
                    dat[pos + 'fed_' + feds[key]] = 0
                for fed in feds_taken:
                    dat[pos + 'fed_' + feds[fed['tile']]] += 1

                # final buildings
                total_buildings = 0
                found_buildings = tree['data']['players'][i]['data']['buildings']
                for key in found_buildings.keys():
                    if key in bad_buildings:
                        if found_buildings[key] > 0:
                            raise ValueError('this is a game with expansions ' + key)
                        continue
                    elif key != 'gf' and key != 'sp':
                        dat[pos + 'build_' + key] = found_buildings[key]
                        total_buildings += found_buildings[key]
                dat[pos + 'num_structures'] = total_buildings

                # research
                tech_score = 0
                found_research = tree['data']['players'][i]['data']['research']
                for key in found_research.keys():
                    if key == 'dip':
                        raise ValueError('this is a game with expansions ' + key)

                    dat[pos + 'research_level_' + key] = found_research[key]
                    if found_research[key] > 2:
                        tech_score += (4 * (found_research[key] - 2))
                dat[pos + 'tech_score'] = tech_score

                # techs taken
                total_techs = 0
                found_techs = tree['data']['players'][i]['data']['tiles']['techs']
                for key in techs.keys():
                    dat[pos + 'tech_taken_' + techs[key]] = False
                for key in adv_techs.keys():
                    dat[pos + 'adv_tech_taken_' + adv_techs[key]] = False
                for tech in found_techs:
                    total_techs += 1
                    name = tech['tile']
                    if name in techs.keys():
                        dat[pos + 'tech_taken_' + techs[name]] = True
                    elif name in adv_techs.keys():
                        dat[pos + 'adv_tech_taken_' + adv_techs[name]] = True
                    else:
                        dat[pos + 'tech_taken_' + adv_techs[name]] = True
                dat[pos + 'total_techs_taken'] = total_techs

                # buildings
                dat = parse_tree_builds(dat, tree, pos, faction)

            dat['average_elo'] = tot_elo / num_players
            dat = pd.DataFrame(dat, index=[0])
            return True, dat, num_players, errors_set
        except:
            errors_set[tree['_id']] = traceback.format_exc()
            return False, "", "", errors_set

    else:
        return False, "", "", errors_set


def parse_jsons():
    with open("game_data_raw.txt", "r") as game_data_raw:

        two_players = None
        three_players = None
        four_players = None

        errors_set = dict()

        lines = game_data_raw.readlines()
        for line in lines:
            game_tree = json.loads(line)
            success, df, num_player, errors_set = parse_tree(game_tree, errors_set)
            if success:
                if num_player == 2:
                    if two_players is not None:
                        two_players = pd.concat([two_players, df], axis=0, join="outer", ignore_index=True)
                    else:
                        two_players = df
                elif num_player == 3:
                    if three_players is not None:
                        three_players = pd.concat([three_players, df], axis=0, join="outer", ignore_index=True)
                    else:
                        three_players = df
                else:
                    if four_players is not None:
                        four_players = pd.concat([four_players, df], axis=0, join="outer", ignore_index=True)
                    else:
                        four_players = df

        two_players.to_pickle("two_players_data")
        three_players.to_pickle("three_players_data")
        four_players.to_pickle("four_players_data")




