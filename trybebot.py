#!/usr/bin/env python3

import urllib #url formatting
import time #to enable timeout
import json
import requests

from urllib.request import urlopen

TOKEN = "967526375:AAEtE0EXObee7jS-3i7ejXO2NpiG9piHQr4"
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
        forcereplykb = force_reply()
        removekb = remove_keyboard()
        options = build_keyboard()
        itemcondition = build_keyboard2()
        emoji = 0

        # items = db.get_items(chat)
        if text == "/start":
            db.update_field(0, chat)
            send_message("Welcome to Trybe! I'm here to help you with your post. Send /createpost to begin. Send /cancel to terminate the service at any time.", chat)
             #set state to 0
            print(str(db.read_state(chat)))
        elif text == "/cancel":
            send_message(text="Process terminated. Send /createpost to restart.", chat_id=chat, reply_markup=removekb)
            db.update_field(0, chat) #reset the state to 0
            db.delete_user(chat)
        elif text == "/createpost":
            db.update_field(0, chat)
            send_message(text="What's your name?", chat_id=chat, reply_markup=forcereplykb)
            print(str(db.read_state(chat)))
        elif text.startswith("/"):
            send_message(text="Invalid command. Send /cancel to cancel this post.", chat_id=chat, reply_markup=removekb)
            continue
        elif str(db.read_state(chat)) == "[0]":
            db.update_field(1, chat, text)
            send_message(text="What's your telegram username?", chat_id=chat, reply_markup=forcereplykb)
            print(str(db.read_state(chat)))
        elif str(db.read_state(chat)) == "[1]":
            db.update_field(2, chat, text)
            send_message(text="Would you like to make an offer or a request today?", chat_id=chat, reply_markup=options)
            print(str(db.read_state(chat)))
        elif str(db.read_state(chat)) == "[2]":
            print(str(db.read_type(chat)))
            if text == "OFFER":
                db.update_field(3, chat, text)
                send_message(text="Give a name for the item or service you are offering!", chat_id=chat, reply_markup=forcereplykb)
            elif text == "REQUEST":
                db.update_field(3, chat, text)
                send_message(text="Give a name for the item or service you are requesting for.", chat_id=chat, reply_markup=forcereplykb)
            else:
                send_message(text="Please choose from the options provided below.", chat_id=chat) #failsafe measure any
            print(str(db.read_state(chat)))
        elif str(db.read_state(chat)) == "[3]":
            if str(db.read_type(chat)) == "['OFFER']":
                db.update_field(6, chat, text)
                send_message(text="Is your item new or used?", chat_id=chat, reply_markup=itemcondition)
            if str(db.read_type(chat)) == "['REQUEST']":
                db.update_field(4, chat, text)
                send_message(text="Give a short description for the item or service you are requesting for.", chat_id=chat, reply_markup=forcereplykb)
            print(str(db.read_state(chat)))
        elif str(db.read_state(chat)) == "[6]":
            db.update_field(4, chat, text)
            send_message(text="Out of 10, what is the condition of the item or the proficiency of your service?", chat_id=chat, reply_markup=forcereplykb)
        elif str(db.read_state(chat)) == "[4]":
            db.update_field(5, chat, text)
            list = []
            index = 0
            for x in range(6):
                list.append(db.get_details(chat, index))
                index += 1

            if str(list[2]) == "['OFFER']": #offer
                emoji = "%E2%9C%A8"
                condition = "/10"
                desc = "Condition:%20"
            else:
                emoji = "%F0%9F%8C%88"
                condition = ""
                desc = "Description:%20"

            # if str(list[1]) == "@":
            #     print(list[1][2])
            #     char = ""
            # else:
            #     char = "@"

            if str(list[4]).strip('[\'\']') == "NA":
                content = emoji + str(list[2]).strip('[\'\']') + "%0A" + "Name:%20" + str(list[0]).strip('[\'\']') + "%0A" + "Username:%20" + str(list[1]).strip('[\'\']') + "%0A" + "Item/Process:%20" + str(list[3]).strip('[\'\']') + "%0A" + desc + str(list[5]).strip('[\'\']') + condition
            else:
                content = emoji + str(list[2]).strip('[\'\']') + "%0A" + "Name:%20" + str(list[0]).strip('[\'\']') + "%0A" + "Username:%20" + str(list[1]).strip('[\'\']') + "%0A" + "Item/Process:%20" + str(list[4]).strip('[\'\']') + "%0A" + desc + str(list[3]).strip('[\'\']') + "; " + str(list[5]).strip('[\'\']') + condition
            print(content)
            uri = "https://api.telegram.org/bot967526375:AAEtE0EXObee7jS-3i7ejXO2NpiG9piHQr4/sendMessage?chat_id=@RUAOK&text=%s" % content
            urlopen(uri)
            list.clear()
            db.delete_user(chat)
            send_message(text="Thank you for being a part of the Trybe community! Your offer/request has successfully been posted to the Trybe Services channel @trybe_services.", chat_id=chat, reply_markup=removekb)
            # print(str(db.read_state(chat)))


        # elif text in items:
        #     keyboard = remove_keyboard()
        #     db.delete_item(text, chat)
        #     items = db.get_items(chat)
        #     send_message("Item cleared.", chat)
        #     message = "\n".join(items) #sends back the list of current items
        #     send_message("TODO:\n"+message, chat, keyboard)
        else:
            send_message("Invalid response. Send /createpost to begin new post.", chat)
            # db.add_item(text, chat)
            # items = db.get_items(chat)
            # send_message("Item added.", chat)
            # message = "\n".join(items) #sends back the list of current items
            # send_message("TODO:\n"+message, chat)



def build_keyboard():
    keyboard = [['OFFER', 'REQUEST']]
    reply_markup = {"keyboard": keyboard, "resize_keyboard": True, "one_time_keyboard": True}
    return json.dumps(reply_markup)

def build_keyboard2():
    keyboard = [['NEW', 'USED']]
    reply_markup = {"keyboard": keyboard, "resize_keyboard": True, "one_time_keyboard": True}
    return json.dumps(reply_markup)

def force_reply():
    reply_markup = {"force_reply": True, "selective": False}
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
