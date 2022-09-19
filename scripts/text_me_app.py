#!/usr/bin/env/ python3
from flask import Flask, request, jsonify, Response
import json
from filelock import Timeout, FileLock
import email, smtplib, ssl
from email.mime.text import MIMEText

GATEWAYS_FILE_PATH = "gateways.json"
PLAYER_DATA_FILE_PATH = "player_data.json"
PLAYER_DATA_LOCK_FILE_PATH = "player_data.json.lock"
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
    subject = "registered for gpstats texts"
    message = "You are registered to receive turn reminder texts for your " + username + " bgs account!"
    link_found = False
    link = ''
    for g in gateways:
        if g.get("country").upper() == country.upper() and g.get("provider").upper() == provider.upper():
            link_found = True
            link = g.get("link")

    link_split = link.split("#")
    receiver_email = link_split[0] + str(number) + link_split[-1]

    account_link = "https://www.boardgamers.space/user/" + username

    # email_body = f"<body>Congratulations! Your <a href='{account_link}'>{username}</a><br> bgs account is registered to receive messages on your turn :)</body>"
    email_body = f"Congratulations! Your {username} bgs account is registered to receive messages on your turn :)"

    msg = MIMEText(email_body, 'html')
    msg['Subject'] = ""
    msg['From'] = sender_email
    msg['To'] = receiver_email
    server = smtplib.SMTP_SSL('smtppro.zoho.com', 465)
    server.login(sender_email, email_password)
    server.sendmail(sender_email, [receiver_email], msg.as_string())
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

    email_body = f"Your {username} bgs account is removed from messaging list"

    msg = MIMEText(email_body, 'html')
    msg['Subject'] = ""
    msg['From'] = sender_email
    msg['To'] = receiver_email
    server = smtplib.SMTP_SSL('smtppro.zoho.com', 465)
    server.login(sender_email, email_password)
    server.sendmail(sender_email, [receiver_email], msg.as_string())
    server.quit()

    return link_found


app = Flask(__name__)


@app.route("/")
def hello():
    return "TextMe Running"


@app.route("/AddMyNumber", methods=['GET', 'PUT'])
def add_number():
    player_data = dict()

    args_dict = request.args.to_dict()
    country = args_dict.get("country")
    if country.upper() not in countries:
        return jsonify("{'result': 'country_not_in_list'}"), 403
    provider = args_dict.get("provider")
    if provider.upper() not in providers:
        return jsonify("{'result': 'provider_not_in_list'}"), 403
    number = args_dict.get("number")
    if not number.isdigit():
        return jsonify("{'result': 'number_has_nondigit_chars'}"), 403
    username = args_dict.get("username")

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
            return jsonify("{'result': 'player_added'}"), 200


@app.route("/RemoveMyNumber", methods=['GET', 'DELETE'])
def remove_number():
    args_dict = request.args.to_dict()

    number = args_dict.get("number")
    if not number.isdigit():
        return jsonify("{'result': 'number_has_nondigit_chars'}"), 403
    username = args_dict.get("username")

    lock = FileLock(PLAYER_DATA_LOCK_FILE_PATH)
    with lock:
        with open(PLAYER_DATA_FILE_PATH) as player_data_file:
            player_data = json.load(player_data_file)

    if username in player_data and str(player_data.get(username).get('number')) == str(number):
        player_data.pop(username)

    with lock:
        with open(PLAYER_DATA_FILE_PATH, "w") as player_data_file:
            json.dump(player_data, player_data_file, indent=4, separators=(',', ': '))
            try:
                text_removed(player_data.get('country'), player_data.get('provider'), player_data.get('number'), username)
            except:
                pass
            return jsonify("{'result': 'player_removed'}"), 200


if __name__ == "__main__":
    app.run()
