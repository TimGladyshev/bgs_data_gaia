#!/usr/bin/env/ python3
import requests
from flask import Flask, request, jsonify, Response, make_response
import json
from filelock import Timeout, FileLock
import email, smtplib, ssl
from email.mime.text import MIMEText
import urllib.parse

GATEWAYS_FILE_PATH = "/home/texter/gateways.json"
PLAYER_DATA_FILE_PATH = "/home/texter/player_data.json"
PLAYER_DATA_LOCK_FILE_PATH = "/home/texter/player_data.json.lock"
# sender_credentials = ('gp.stats.dev@gmail.com', 'dlghwnjsgsiuconu')
sender_credentials = ('tim@gpstats.dev', 'kDxs EWrm E8LC')

# gateways json is list of jsons with provider, country, link
# special notes are not handled and corresponding providers will not work
countries = set()
providers = set()
with open(GATEWAYS_FILE_PATH) as gateways_file:
    gateways = json.load(gateways_file)
    for g in gateways:
        countries.add(g.get("country").upper())
        providers.add(g.get("provider").upper())


def text_registered(country, provider, number, username):
    sender_email, email_password = sender_credentials
    link_found = False
    link = ''
    for g in gateways:
        if g.get("country").upper() == country.upper() and g.get("provider").upper() == provider.upper():
            link_found = True
            link = g.get("link")

    link_split = link.split("#")
    receiver_email = link_split[0] + str(number) + link_split[-1]

    games_link = f"https://www.gpstats.dev/textme/RemoveMyNumber?number={number}&username={urllib.parse.quote_plus(username)}"

    body_1 = f"Your {username} bgs account is registered to receive turn reminders at this number :)"
    body_2 = games_link

    msg1 = MIMEText(body_1, 'plain')
    msg1['Subject'] = "Congratulations!"
    msg1['From'] = sender_email
    msg1['To'] = receiver_email
    msg2 = MIMEText(body_2, 'plain')
    msg2['Subject'] = "Remove me"
    msg2['From'] = sender_email
    msg2['To'] = receiver_email

    server = smtplib.SMTP_SSL('smtppro.zoho.com', 465)

    try:
        server.login(sender_email, email_password)
        server.sendmail(sender_email, [receiver_email], msg1.as_string())
        server.sendmail(sender_email, [receiver_email], msg2.as_string())
    finally:
        server.quit()

    return link_found


def text_removed(country, provider, number, username):
    sender_email, email_password = sender_credentials
    link_found = False
    link = ''
    for g in gateways:
        if g.get("country").upper() == country.upper() and g.get("provider").upper() == provider.upper():
            link_found = True
            link = g.get("link")

    link_split = link.split("#")
    receiver_email = link_split[0] + str(number) + link_split[-1]

    games_link = f"https://www.gpstats.dev/textme/AddMyNumber?country={urllib.parse.quote_plus(country)}&provider={urllib.parse.quote_plus(provider)}&number={number}&username={urllib.parse.quote_plus(username)}"

    body_1 = f"Your {username} bgs account has been removed"
    body_2 = games_link

    msg1 = MIMEText(body_1, 'plain')
    msg1['Subject'] = "Goodbye!"
    msg1['From'] = sender_email
    msg1['To'] = receiver_email
    msg2 = MIMEText(body_2, 'plain')
    msg2['Subject'] = "Add me back"
    msg2['From'] = sender_email
    msg2['To'] = receiver_email

    server = smtplib.SMTP_SSL('smtppro.zoho.com', 465)

    try:
        server.login(sender_email, email_password)
        server.sendmail(sender_email, [receiver_email], msg1.as_string())
        server.sendmail(sender_email, [receiver_email], msg2.as_string())
    finally:
        server.quit()

    return link_found


def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response


def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


app = Flask(__name__)


@app.route("/")
def hello():
    return "TextMe Running"


@app.route("/AddMyNumber", methods=['GET', 'PUT'])
def add_number():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    else:
        player_data = dict()

        args_dict = request.args.to_dict()
        country = args_dict.get("country")
        if country.upper() not in countries:
            return _corsify_actual_response(jsonify("{'result': 'country_not_in_list'}")), 403
        provider = args_dict.get("provider")
        if provider.upper() not in providers:
            return _corsify_actual_response(jsonify("{'result': 'provider_not_in_list'}")), 403
        number = args_dict.get("number")
        if not number.isdigit():
            return _corsify_actual_response(jsonify("{'result': 'number_has_nondigit_chars'}")), 403
        username = args_dict.get("username").lower()

        lock = FileLock(PLAYER_DATA_LOCK_FILE_PATH)
        with lock:
            with open(PLAYER_DATA_FILE_PATH) as player_data_file:
                player_data = json.load(player_data_file)

        if username in player_data:
            player_data.pop(username)

        new_data = {
            "username": username,
            "country": country,
            "provider": provider,
            "number": number
        }
        player_data[username] = new_data
        with lock:
            with open(PLAYER_DATA_FILE_PATH, "w") as player_data_file:
                json.dump(player_data, player_data_file, indent=4, separators=(',', ': '))
                try:
                    text_registered(country, provider, number, username)
                except:
                    pass
                return _corsify_actual_response(jsonify("{'result': 'player_added'}")), 200


@app.route("/RemoveMyNumber", methods=['GET', 'DELETE'])
def remove_number():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    else:
        args_dict = request.args.to_dict()

        number = args_dict.get("number")
        if not number.isdigit():
            return _corsify_actual_response(jsonify("{'result': 'number_has_nondigit_chars'}")), 403
        username = args_dict.get("username").lower()

        lock = FileLock(PLAYER_DATA_LOCK_FILE_PATH)
        with lock:
            with open(PLAYER_DATA_FILE_PATH) as player_data_file:
                player_data = json.load(player_data_file)

        cur_player_data = None
        if username in player_data and str(player_data.get(username).get('number')) == str(number):
            cur_player_data = player_data.get(username)
            player_data.pop(username)

        with lock:
            with open(PLAYER_DATA_FILE_PATH, "w") as player_data_file:
                json.dump(player_data, player_data_file, indent=4, separators=(',', ': '))
                try:
                    if cur_player_data:
                        text_removed(cur_player_data.get('country'), cur_player_data.get('provider'),
                                     cur_player_data.get('number'), username)
                except:
                    pass
                return _corsify_actual_response(jsonify("{'result': 'player_removed'}")), 200


@app.route("/CheckUsername", methods=['GET', 'OPTIONS'])
def check_username():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    else:
        args_dict = request.args.to_dict()
        username = args_dict.get("username")

        resp = requests.get(
            url='https://www.boardgamers.space/user/' + username)

        return _corsify_actual_response(jsonify(resp.ok)), resp.status_code


if __name__ == "__main__":
    app.run()
