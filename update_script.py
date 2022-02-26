from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType
import requests
from time import sleep
import asyncio
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import json
from subprocess import check_output
import traceback
import shutil
import os
from subprocess import call
import time

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

factions = {
    "terrans",
    "lantids",
    "hadsch-hallas",
    "ivits",
    "baltaks",
    "geodens",
    "xenos",
    "gleens",
    "ambas",
    "taklons",
    "bescods",
    "firaks",
    "itars",
    "nevlas"
}


def update_all():
    op = webdriver.ChromeOptions()
    op.add_argument('headless')
    op.add_argument('--headless')
    op.add_argument('--no-sandbox')
    op.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install(), options=op)

    url_games = 'https://www.boardgamers.space/boardgame/gaia-project/games'

    games_set = set()
    new_names = set()

    with open("/var/www/TimGladyshev/gaia_stats/data/game_names.txt", "r") as names_file:
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

    # list of names items
    game_names = driver.find_elements_by_class_name("game-name")

    with open("/var/www/TimGladyshev/gaia_stats/data/game_names.txt", "a") as names_file:

        for name in game_names:
            n = name.text
            if n not in games_set:
                new_names.add(n)
                names_file.write(n + '\n')

        for i in range((num_games_found - len(games_set)) // 10):
            try:
                next_button.click()
                sleep(.1)

                # wait for JS to load -> elements are same, only text and class are updated
                while driver.execute_script("return document.readyState") != "complete":
                    sleep(.05)

                next_button = driver.find_elements_by_class_name("page-link")[-2]

                game_names = driver.find_elements_by_class_name("game-name")

                for name in game_names:
                    n = name.text
                    if n not in games_set:
                        new_names.add(n)
                        names_file.write(n + '\n')
            except:
                break

    names_file.close()
    driver.close()

    errors_set = dict()
    two_players = pd.read_csv("/var/www/TimGladyshev/gaia_stats/data/two_players_data.csv")
    three_players = pd.read_csv("/var/www/TimGladyshev/gaia_stats/data/three_players_data.csv")
    four_players = pd.read_csv("/var/www/TimGladyshev/gaia_stats/data/four_players_data.csv")

    base_url = "https://www.boardgamers.space/api/game/"
    with requests.Session() as session:
        for game_name in new_names:
            with session.get(base_url + game_name) as response:
                if response.status_code != 200:
                    continue

                game_tree = response.json()
                # game_tree = json.loads(data)
                success, df, num_player, errors_set = parse_tree(game_tree, errors_set)
                if success:
                    if num_player == 2:
                        two_players = pd.concat([two_players, df], axis=0, join="outer", ignore_index=True)
                    elif num_player == 3:
                        three_players = pd.concat([three_players, df], axis=0, join="outer", ignore_index=True)
                    else:
                        four_players = pd.concat([four_players, df], axis=0, join="outer", ignore_index=True)

    two_players = two_players.drop_duplicates(subset=['id'])
    three_players = three_players.drop_duplicates(subset=['id'])
    four_players = four_players.drop_duplicates(subset=['id'])

    err_types = set(errors_set.values())
    err_to_count = {}
    for err in err_types:
        count = sum(map(str(err).__eq__, errors_set.values()))
        err_to_count[err] = count

    error_string = ""
    for err in err_types:
        for key in errors_set.keys():
            if errors_set[key] == err:
                error_string += 'Game Name: ' + key + ' Total Error Count: ' + str(err_to_count[err]) + '<br>'
                error_string += err
                error_string += '<br>------'
                break

    with open('/var/www/TimGladyshev/gaia_stats/errors/index.html', 'w') as file:
        html = "<html><head></head><body><p>" + error_string + "</p></body></html>"
        file.write(html)

    with open('/var/www/TimGladyshev/gaia_stats/js/vars.js', 'w') as js_file:
        js = 'const parsed = ' + str(len(two_players) + len(three_players) + len(four_players)) + ';\n' + 'const ' \
                                                                                                          'millis = ' \
             + str(round(time.time() * 1000))
        js_file.write(js)

    two_players.to_csv("/var/www/TimGladyshev/gaia_stats/data/two_players_data.csv")
    three_players.to_csv("/var/www/TimGladyshev/gaia_stats/data/three_players_data.csv")
    four_players.to_csv("/var/www/TimGladyshev/gaia_stats/data/four_players_data.csv")

    make_plots(two_players, three_players, four_players)


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
                        # havent cought expansion till now?
                        if found_research[key] > 0:
                            # normal games seem to have this key now also
                            raise ValueError('this is a game with expansions ' + key)
                    else:
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


def plot_adv_freq_remote(num_players, dat_x):
    for faction in factions:
        factions_pos = []
        for pos in range(num_players):
            dat = dat_x[dat_x['pos_' + str(pos + 1) + '_dropped'] == False]
            factions_pos.append(dat[dat["pos_" + str(pos + 1) + "_faction"] == faction])
        factions_in = pd.concat(factions_pos, ignore_index=True)

        fig = go.Figure()

        x = []
        for val in adv_techs.values():
            x.append(val)

        # get overall percents for printing
        overall = [0] * len(adv_techs.values())
        for i in range(num_players):
            for j, tech in enumerate(adv_techs.values()):
                df = factions_pos[i]

                # get all games where tech is present
                slots_df = []
                tech_slots = [
                    "tech_adv-terra",
                    "tech_adv-nav",
                    "tech_adv-int",
                    "tech_adv-gaia",
                    "tech_adv-eco",
                    "tech_adv-sci"
                ]
                for slot in tech_slots:
                    slots_df.append(factions_in[factions_in[slot] == tech])
                df_avail = pd.concat(slots_df, ignore_index=True)

                freq_taken = len(df[df['pos_' + str(i + 1) + '_adv_tech_taken_' + tech] == True]) / len(df_avail)
                overall[j] += freq_taken

        for i in range(num_players):
            y = []
            info = []
            for j, tech in enumerate(adv_techs.values()):
                df = factions_pos[i]

                # get all games where tech is present
                slots_df = []
                tech_slots = [
                    "tech_adv-terra",
                    "tech_adv-nav",
                    "tech_adv-int",
                    "tech_adv-gaia",
                    "tech_adv-eco",
                    "tech_adv-sci"
                ]
                for slot in tech_slots:
                    slots_df.append(factions_in[factions_in[slot] == tech])
                df_avail = pd.concat(slots_df, ignore_index=True)

                freq_taken = len(df[df['pos_' + str(i + 1) + '_adv_tech_taken_' + tech] == True]) / len(df_avail)
                y.append(round(freq_taken * 100, 3))
                info.append(round(((freq_taken / overall[j]) * 100), 3))
            fig.add_trace(go.Bar(x=x, y=y, name='rank_' + str(i + 1),
                                 hovertemplate=
                                 '<br><b>Rank</b>: ' + str(i + 1) +
                                 '<br><b>Tech</b>: %{x}' +
                                 '<br><b>% Taken if Available</b>: %{y}' +
                                 '<br><b>% Rank if Taken</b>: %{text}' +
                                 '<br><b>% Rank overall</b>: ' + str(
                                     round((len(factions_pos[i]) / len(factions_in)) * 100, 2)) +
                                 '<extra></extra>',
                                 text=info,
                                 texttemplate=''))

        title_text = "Frequency Advanced Tech Tile is Taken and the Resulting Rank Distribution: " + faction

        fig.update_layout(uniformtext_minsize=100000, uniformtext_mode='hide')
        fig.update_layout(barmode='stack')
        fig.update_xaxes(categoryorder='total ascending')
        fig.update_layout(title_text=title_text, xaxis_title="Advanced Tech",
                          yaxis_title="Percent of Games Taken")

        fig.write_html(
            "/var/www/TimGladyshev/gaia_stats/" + str(
                num_players) + "p/adv_techs_analysis/taken_freq/" + faction + ".html")


def plot_adv_track_remote(num_players, dat_x):
    for faction in factions:

        tech_slots = [
            "tech_adv-terra",
            "tech_adv-nav",
            "tech_adv-int",
            "tech_adv-gaia",
            "tech_adv-eco",
            "tech_adv-sci"
        ]

        factions_pos = []
        for pos in range(num_players):
            dat = dat_x[dat_x['pos_' + str(pos + 1) + '_dropped'] == False]
            factions_pos.append(dat[dat["pos_" + str(pos + 1) + "_faction"] == faction])
        factions_in = pd.concat(factions_pos, ignore_index=True)

        techs = list(adv_techs.values())

        slot_scores = []
        for i in range(len(tech_slots) + 1):
            slot_scores.append([])

        game_nums = []
        for i in range(len(tech_slots) + 1):
            game_nums.append([])

        fig = go.Figure()

        for tech in adv_techs.values():
            not_taken_score = 0
            not_taken_amount = 0
            for i, slot in enumerate(tech_slots):
                taken_score = 0
                taken_amount = 0
                for pos in range(num_players):
                    df = factions_pos[pos]
                    df = df[df[slot] == tech]
                    df_not_taken = df[df['pos_' + str(pos + 1) + "_adv_tech_taken_" + tech] == False]
                    not_taken_score += df_not_taken['pos_' + str(pos + 1) + "_score"].mean()
                    not_taken_amount += len(df_not_taken)
                    df_taken = df[df['pos_' + str(pos + 1) + "_adv_tech_taken_" + tech] == True]
                    taken_score += df_taken['pos_' + str(pos + 1) + "_score"].mean()
                    taken_amount += len(df_taken)
                slot_scores[i].append(taken_score / num_players)
                game_nums[i].append(taken_amount)
            slot_scores[-1].append(not_taken_score / 6 / num_players)
            game_nums[-1].append(not_taken_amount)

        tech_slots.append("tech_adv-not_taken")

        colors = [
            'rgba(165, 42, 42, .9)',
            'rgba(112, 128, 144, .9)',
            'rgba(38, 166, 91, .9)',
            'rgba(191, 85, 236, .9)',
            'rgba(255, 215, 0, .9)',
            'rgba(3, 138, 255, .9)',
            'rgba(242, 38, 19, .9)'

        ]

        for i, slot in enumerate(tech_slots):
            fig.add_trace(go.Scatter(
                x=slot_scores[i],
                y=techs,
                mode="markers",
                marker_color=colors[i],
                name=slot.split('-')[1],
                hovertemplate=
                '<br><b>Position</b>: ' + slot.split('-')[1] +
                '<br><b>Tech</b>: %{y}' +
                '<br><b>Ave Score</b>: %{x}' +
                '<br><b>Num Found</b>: %{text}' +
                '<extra></extra>',
                text=game_nums[i]
            ))

        average_score_overall = 0
        for j in range(num_players):
            df = factions_pos[j]
            average_score_overall += df['pos_' + str(j + 1) + "_score"].mean()
        average_score_overall = average_score_overall / num_players

        fig.add_vline(x=average_score_overall, line_dash="dot", line_width=2,
                      annotation_text="overall average: " + str(round(average_score_overall, 2))
                      )

        fig.update_layout(title="Advanced Technology Impact on Average Score by Track Taken: " + faction,
                          xaxis_title="Average Score",
                          yaxis_title="Advanced Tech")

        fig.write_html(
            "/var/www/TimGladyshev/gaia_stats/" + str(
                num_players) + "p/adv_techs_analysis/pos_on_score/" + faction + ".html")


def plot_base_track_remote(num_players, dat_x):
    for faction in factions:

        tech_slots = [
            "tech_terra",
            "tech_nav",
            "tech_int",
            "tech_gaia",
            "tech_eco",
            "tech_sci"
        ]

        factions_pos = []
        for pos in range(num_players):
            dat = dat_x[dat_x['pos_' + str(pos + 1) + '_dropped'] == False]
            factions_pos.append(dat[dat["pos_" + str(pos + 1) + "_faction"] == faction])
        factions_in = pd.concat(factions_pos, ignore_index=True)

        techs_list = list(techs.values())

        slot_scores = []
        for i in range(len(tech_slots) + 1):
            slot_scores.append([])

        game_nums = []
        for i in range(len(tech_slots) + 1):
            game_nums.append([])

        fig = go.Figure()

        for tech in techs.values():
            not_taken_score = 0
            not_taken_amount = 0
            for i, slot in enumerate(tech_slots):
                taken_score = 0
                taken_amount = 0
                for pos in range(num_players):
                    df = factions_pos[pos]
                    df = df[df[slot] == tech]
                    df_not_taken = df[df['pos_' + str(pos + 1) + "_tech_taken_" + tech] == False]
                    not_taken_score += df_not_taken['pos_' + str(pos + 1) + "_score"].mean()
                    not_taken_amount += len(df_not_taken)
                    df_taken = df[df['pos_' + str(pos + 1) + "_tech_taken_" + tech] == True]
                    taken_score += df_taken['pos_' + str(pos + 1) + "_score"].mean()
                    taken_amount += len(df_taken)
                slot_scores[i].append(taken_score / num_players)
                game_nums[i].append(taken_amount)
            slot_scores[-1].append(not_taken_score / 6 / num_players)
            game_nums[-1].append(not_taken_amount)

        tech_slots.append("tech_not_taken")

        colors = [
            'rgba(165, 42, 42, .9)',
            'rgba(112, 128, 144, .9)',
            'rgba(38, 166, 91, .9)',
            'rgba(191, 85, 236, .9)',
            'rgba(255, 215, 0, .9)',
            'rgba(3, 138, 255, .9)',
            'rgba(242, 38, 19, .9)'

        ]

        for i, slot in enumerate(tech_slots):
            fig.add_trace(go.Scatter(
                x=slot_scores[i],
                y=techs_list,
                mode="markers",
                marker_color=colors[i],
                name=slot,
                hovertemplate=
                '<br><b>Position</b>: ' + slot +
                '<br><b>Tech</b>: %{y}' +
                '<br><b>Ave Score</b>: %{x}' +
                '<br><b>Num Found</b>: %{text}' +
                '<extra></extra>',
                text=game_nums[i]
            ))

        average_score_overall = 0
        for j in range(num_players):
            df = factions_pos[j]
            average_score_overall += df['pos_' + str(j + 1) + "_score"].mean()
        average_score_overall = average_score_overall / num_players

        fig.add_vline(x=average_score_overall, line_dash="dot", line_width=2,
                      annotation_text="overall average: " + str(round(average_score_overall, 2)))

        text = "Basic Technology Impact on Average Score by Track Taken: " + faction
        fig.update_layout(title=text,
                          xaxis_title="Average Score",
                          yaxis_title="Tech")

        fig.write_html(
            "/var/www/TimGladyshev/gaia_stats/" + str(
                num_players) + "p/base_tech_analysis/pos_on_score/" + faction + ".html")


def plot_base_freq_remote(num_players, dat_x):
    for faction in factions:
        factions_pos = []
        for pos in range(num_players):
            dat = dat_x[dat_x['pos_' + str(pos + 1) + '_dropped'] == False]
            factions_pos.append(dat[dat["pos_" + str(pos + 1) + "_faction"] == faction])
        factions_in = pd.concat(factions_pos, ignore_index=True)

        if len(factions_in) == 0:
            factions_in.head()
            raise ValueError('faction not found: ' + faction)

        fig = go.Figure()

        x = []
        for val in techs.values():
            x.append(val)

        # get overall percents for printing
        overall = [0] * len(techs.values())
        for i in range(num_players):
            for j, tech in enumerate(techs.values()):
                df = factions_pos[i]

                freq_taken = len(df[df['pos_' + str(i + 1) + '_tech_taken_' + tech] == True]) / len(factions_in)
                overall[j] += freq_taken

        for i in range(num_players):
            y = []
            info = []
            for j, tech in enumerate(techs.values()):
                df = factions_pos[i]

                freq_taken = len(df[df['pos_' + str(i + 1) + '_tech_taken_' + tech] == True]) / len(factions_in)
                y.append(round(freq_taken * 100, 3))
                info.append(round(((freq_taken / overall[j]) * 100), 3))
            fig.add_trace(go.Bar(x=x, y=y, name='rank_' + str(i + 1),
                                 hovertemplate=
                                 '<br><b>Rank</b>: ' + str(i + 1) +
                                 '<br><b>Tech</b>: %{x}' +
                                 '<br><b>% Taken for Rank</b>: %{y}' +
                                 '<br><b>% Rank if Taken</b>: %{text}' +
                                 '<br><b>% Rank overall</b>: ' + str(
                                     round((len(factions_pos[i]) / len(factions_in)) * 100, 2)) +
                                 '<extra></extra>',
                                 text=info,
                                 texttemplate=''))

        title_text = "Frequency Basic Tech Tile is Taken and the Resulting Rank Distribution: " + faction

        fig.update_layout(uniformtext_minsize=100000, uniformtext_mode='hide')
        fig.update_layout(barmode='stack')
        fig.update_xaxes(categoryorder='total ascending')
        fig.update_layout(title_text=title_text, xaxis_title="Basic Tech",
                          yaxis_title="Percent of Games Taken")

        fig.write_html(
            "/var/www/TimGladyshev/gaia_stats/" + str(
                num_players) + "p/base_tech_analysis/taken_freq/" + faction + ".html")


def plot_r1_structs_remote(num_players, dat_x):
    for faction in factions:
        factions_pos = []
        for pos in range(num_players):
            dat = dat_x

            # select faction
            dat = dat[dat["pos_" + str(pos + 1) + "_faction"] == faction]

            # remove dropped players
            dat = dat[dat['pos_' + str(pos + 1) + '_dropped'] == False]

            # labels
            prefix = "pos_" + str(pos + 1) + '_buildings_r_1'
            structs_class = 'r1_structs_class_' + faction
            structs_exact = 'r1_structs_exact_' + faction
            over_all_score = 'ave_score_' + faction
            over_all_elo = 'ave_elo_' + faction

            # get scores and elos
            dat[over_all_score] = dat['pos_' + str(pos + 1) + '_score']
            dat[over_all_elo] = dat['pos_' + str(pos + 1) + '_elo']

            # structs placed
            dat[prefix + '_PI'] = pd.to_numeric(dat[prefix + '_PI'], downcast='integer')
            dat[prefix + '_ac1'] = pd.to_numeric(dat[prefix + '_ac1'], downcast='integer')
            dat[prefix + '_ac2'] = pd.to_numeric(dat[prefix + '_ac2'], downcast='integer')
            dat[prefix + '_lab'] = pd.to_numeric(dat[prefix + '_lab'], downcast='integer')
            dat[prefix + '_ts'] = pd.to_numeric(dat[prefix + '_ts'], downcast='integer')
            dat[prefix + '_m'] = pd.to_numeric(dat[prefix + '_m'], downcast='integer')

            # create general structs catergory
            dat.loc[dat[prefix + '_PI'] > 0, structs_class] = 'PI'
            dat.loc[dat[prefix + '_ac1'] > 0, structs_class] = 'ac1'
            dat.loc[dat[prefix + '_ac2'] > 0, structs_class] = 'ac2'
            dat.loc[
                (dat[prefix + '_lab'] > 0) &
                (dat[prefix + '_PI'] == 0) &
                (dat[prefix + '_ac1'] == 0) &
                (dat[prefix + '_ac2'] == 0)
                , structs_class] = 'lab'

            dat.loc[
                (dat[prefix + '_ts'] > 0) &
                (dat[prefix + '_lab'] == 0) &
                (dat[prefix + '_PI'] == 0) &
                (dat[prefix + '_ac1'] == 0) &
                (dat[prefix + '_ac2'] == 0)
                , structs_class] = 'ts'

            dat.loc[
                (dat[prefix + '_ts'] == 0) &
                (dat[prefix + '_lab'] == 0) &
                (dat[prefix + '_PI'] == 0) &
                (dat[prefix + '_ac1'] == 0) &
                (dat[prefix + '_ac2'] == 0)
                , structs_class] = 'm'

            # create exact category
            dat[structs_exact] = [" " +
                                  str(m) + '-m_' +
                                  str(ts) + '-ts_' +
                                  str(lab) + '-lab_' +
                                  str(PI) + '-pi_' +
                                  str(ac1) + '-ac1_' +
                                  str(ac2) + '-ac2'
                                  for m, ts, lab, PI, ac1, ac2 in zip(
                    dat[prefix + '_m'],
                    dat[prefix + '_ts'],
                    dat[prefix + '_lab'],
                    dat[prefix + '_PI'],
                    dat[prefix + '_ac1'],
                    dat[prefix + '_ac2'])
                                  ]

            factions_pos.append(dat)

        factions_in = pd.concat(factions_pos, ignore_index=True)

        unique_starts = factions_in[[structs_exact, structs_class, over_all_score, over_all_elo]]
        unique_starts['class_counts'] = 0
        counts = unique_starts.groupby(structs_exact)['class_counts'].transform('count').to_frame()
        unique_starts = unique_starts[[structs_exact, structs_class, over_all_score, over_all_elo]]
        unique_starts = pd.concat([unique_starts, counts], axis=1)
        unique_starts = unique_starts.groupby([structs_class, structs_exact]).mean().reset_index()
        unique_starts['class_counts'] = pd.to_numeric(unique_starts['class_counts'], downcast='integer')

        # remove really low scores
        # unique_starts = unique_starts[(np.abs(stats.zscore(unique_starts[over_all_score])) > 2)]
        unique_starts = unique_starts[unique_starts[over_all_score].between(unique_starts[over_all_score].quantile(.15),
                                                                            unique_starts[over_all_score].quantile(1))]

        # get average score
        midpoint = 0
        for i in range(num_players):
            midpoint += np.mean(dat_x[dat_x['pos_' + str(i + 1) + '_dropped'] == False]['pos_' + str(i + 1) + '_score'])
        midpoint /= num_players

        # midpoint is average for all factions overall - but color ends are highest and lowest score by that faction
        fig = px.treemap(unique_starts,
                         path=[px.Constant('R1 Structures: Frequency and Overall Score for ' + faction), structs_class,
                               structs_exact], values='class_counts',
                         color=over_all_score, hover_data=[over_all_elo],
                         color_continuous_scale='RdBu',
                         color_continuous_midpoint=midpoint
                         )
        fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))
        fig.update_layout(
            title_text="R1 Structures: Frequency and Impact on Score Relative to All Factions Average (" + str(
                round(midpoint, 2)) + "): " + faction)

        fig.write_html(
            "/var/www/TimGladyshev/gaia_stats/" + str(
                num_players) + "p/r1_structs_analysis/freq_and_score/" + faction + ".html")


def make_plots(two_players, three_players, four_players):
    plot_adv_freq_remote(2, two_players)
    plot_adv_freq_remote(3, three_players)
    plot_adv_freq_remote(4, four_players)

    plot_adv_track_remote(2, two_players)
    plot_adv_track_remote(3, three_players)
    plot_adv_track_remote(4, four_players)

    plot_r1_structs_remote(2, two_players)
    plot_r1_structs_remote(3, three_players)
    plot_r1_structs_remote(4, four_players)

    plot_base_track_remote(2, two_players)
    plot_base_track_remote(3, three_players)
    plot_base_track_remote(4, four_players)

    plot_base_freq_remote(2, two_players)
    plot_base_freq_remote(3, three_players)
    plot_base_freq_remote(4, four_players)


def main():
    update_all()


if __name__ == '__main__':
    main()
