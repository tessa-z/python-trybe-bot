import urllib
import json
import requests

from urllib import parse

TOKEN = "PLACEHOLDER"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)


def get_url(url):  # downloads content from url
    response = requests.get(url)
    content = response.content.decode("utf8")  # decode for python compatibility
    return content


def send_message(text, chat_id, reply_markup=None):  # /sendMessage API with text and chat ID
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)


def get_json_from_url(url):  # parse content string into python dictionary
    content = get_url(url)
    js = json.loads(content)  # loads -> load String
    return js


def get_updates(offset=None):  # /getUpdates from tele API
    url = URL + "getUpdates?timeout=100"  # long polling
    if offset:
        url += "&offset={}".format(offset)  # further args are marked with &
    js = get_json_from_url(url)
    return js


def get_last_update_id(updates):
    update_ids = []  # initilizing a Python list
    for update in updates["result"]:  # looping through updates in result list
        update_ids.append(int(update["update_id"]))  # append the update id to empty list
    return max(update_ids)


def get_last_chat_id_and_text(updates):  # gets chat ID and message of most recent msg
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return text, chat_id
