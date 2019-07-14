#!/usr/bin/env python3

import urllib #url formatting
import time #to enable timeout
import json
import requests

TOKEN = "889358891:AAEiumVQ-7qQasI9g26JsuSTderu8_CLeqg"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

from dbhelper import DBHelper

db = DBHelper()


def get_url(url): #downloads content from url
    response = requests.get(url)
    content = response.content.decode("utf8") #decode for python compatibility
    return content


def get_json_from_url(url): #parse content string into python dictionary
    content = get_url(url)
    js = json.loads(content) #loads -> load String
    return js


def get_updates(offset=None): #/getUpdates from tele API
    url = URL + "getUpdates?timeout=100" #long polling
    if offset:
        url += "&offset={}".format(offset) #further args are marked with &
    js = get_json_from_url(url)
    return js


def get_last_update_id(updates):
    update_ids = [] #initilizing a Python list
    for update in updates["result"]: #looping through updates in result list
        update_ids.append(int(update["update_id"])) #append the update id to empty list
    return max(update_ids)


def get_last_chat_id_and_text(updates): #gets chat ID and message of most recent msg
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


def handle_updates(updates):
    for update in updates["result"]:
        text = update["message"]["text"]
        chat = update["message"]["chat"]["id"]
        print(chat)
        items = db.get_items(chat)
        if text == "/completed":
            keyboard = build_keyboard(items)
            send_message("Select an item to mark complete.", chat, keyboard)
        elif text == "/start":
            send_message("Welcome, I'm your personal todo list management bot. Send me a task you would like to add to your todo list! To mark an item as completed, send /completed to select item.", chat)
        elif text.startswith("/"):
            send_message("Invalid command. Send /completed to mark a task complete.", chat)
            continue
        elif text in items:
            keyboard = remove_keyboard()
            db.delete_item(text, chat)
            items = db.get_items(chat)
            send_message("Item cleared.", chat)
            message = "\n".join(items) #sends back the list of current items
            send_message("TODO:\n"+message, chat, keyboard)
        else:
            db.add_item(text, chat)
            items = db.get_items(chat)
            send_message("Item added.", chat)
            message = "\n".join(items) #sends back the list of current items
            send_message("TODO:\n"+message, chat)



def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)


def remove_keyboard():
    reply_markup = {"remove_keyboard": True}
    return json.dumps(reply_markup)

def send_message(text, chat_id, reply_markup=None): #/sendMessage API with text and chat ID
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)


def main():
    db.setup()
    last_update_id = None
    while True:
        updates = get_updates(last_update_id) #keeps checking for the id with one bigger than the prev
        # print(len(updates["result"]))
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            handle_updates(updates)
        time.sleep(0.5)


if __name__ == '__main__':
    main()
