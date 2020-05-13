#!/usr/bin/env python3

import urllib  # url formatting
import time  # to enable timeout
import json
import requests
import messages
import database

from urllib.request import urlopen
from urllib.parse import quote

TOKEN = "967526375:AAEtE0EXObee7jS-3i7ejXO2NpiG9piHQr4"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

convo = messages.Messages()
db = database.FirebaseHelper()


def get_url(url):  # downloads content from url
    response = requests.get(url)
    content = response.content.decode("utf8")  # decode for python compatibility
    return content


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
    return (text, chat_id)


def handle_updates(updates):
    # print(updates)
    for update in updates["result"]:
        user_input = update["message"]["text"]
        chat_id = update["message"]["chat"]["id"]
        forcereplykb = force_reply()
        removekb = remove_keyboard()
        options = build_keyboard()
        itemcondition = build_keyboard2()  # extract this into a setup function

        if user_input == "/start":
            db.update_state(chat_id, 0)
            send_message(text=convo.welcome, chat_id=chat_id)
        elif user_input == "/cancel":
            send_message(text=convo.process_terminated, chat_id=chat_id, reply_markup=removekb)
            db.update_state(chat_id, 0)  # reset the state to 0
            db.delete_pending_post(chat_id)
            print(str(db.read_state(chat_id)))
        elif user_input == "/createpost":
            db.update_state(chat_id, 0)
            db.update_data(chat_id, "command", user_input)
            send_message(text=convo.ask_name, chat_id=chat_id, reply_markup=forcereplykb)
            print(str(db.read_state(chat_id)))
        elif user_input == "/checkpost":
            # must check that users are not in the middle of constructing a post
            db.update_data(chat_id, "command", user_input)
            db.update_data(chat_id, "state", 0)
            send_message(text=convo.check_post, chat_id=chat_id, reply_markup=forcereplykb)
        elif user_input == "/markpost":
            db.update_data(chat_id, "command", user_input)
            db.update_data(chat_id, "state", 0)
            send_message(text=convo.mark_post, chat_id=chat_id, reply_markup=forcereplykb)
        elif user_input.startswith("/"):
            send_message(text=convo.invalid_command, chat_id=chat_id, reply_markup=removekb)
            continue
        elif db.read_data_pending(chat_id, "command") == "/checkpost":
            prev_conversation_state = db.read_state(chat_id)
            if prev_conversation_state == 0:
                is_expired = db.read_data_history(user_input, "expired")
                if is_expired is not None:
                    if is_expired == "false":
                        send_message(text=convo.check_post_not_expired, chat_id=chat_id)
                    elif is_expired == "true":
                        send_message(text=convo.check_post_expired, chat_id=chat_id)
                    else:
                        send_message(text=convo.system_error, chat_id=chat_id)
                else:
                    send_message(text=convo.system_error, chat_id=chat_id)
            else:
                send_message(text=convo.system_error, chat_id=chat_id)
            db.delete_pending_activity(chat_id)
        elif db.read_data_pending(chat_id, "command") == "/markpost":
            prev_conversation_state = db.read_state(chat_id)
            if prev_conversation_state == 0:
                # check if the person is the owner of the post, otherwise not authorised
                owner_id = db.read_data_history(user_input, "chat_id")
                if chat_id == owner_id:
                    db.update_history_mark_expired(user_input)
                    send_message(text=convo.mark_post_success, chat_id=chat_id)
                else:
                    send_message(text=convo.unauthorised_edit, chat_id=chat_id)
                db.delete_pending_activity(chat_id)
            else:
                send_message(text=convo.system_error, chat_id=chat_id)
        else:
            prev_conversation_state = db.read_state(chat_id)
            if prev_conversation_state == 0:
                db.update_data(chat_id, "name", user_input)
                send_message(text=convo.ask_username, chat_id=chat_id, reply_markup=forcereplykb)
                db.update_state(chat_id, 1)
                print(str(db.read_state(chat_id)))
            elif prev_conversation_state == 1:
                db.update_data(chat_id, "username", user_input)
                send_message(text=convo.ask_type, chat_id=chat_id, reply_markup=options)
                db.update_state(chat_id, 2)
                print(str(db.read_state(chat_id)))
            elif prev_conversation_state == 2:
                if user_input == "OFFER":
                    db.update_data(chat_id, "type", user_input)
                    send_message(text=convo.ask_offer_item_name, chat_id=chat_id, reply_markup=forcereplykb)
                    db.update_state(chat_id, 3)
                elif user_input == "REQUEST":
                    db.update_data(chat_id, "type", user_input)
                    send_message(text=convo.ask_request_item_name, chat_id=chat_id, reply_markup=forcereplykb)
                    db.update_state(chat_id, 3)
                else:
                    send_message(text=convo.invalid_type, chat_id=chat_id)  # fail safe measure any
                print(str(db.read_state(chat_id)))
            elif prev_conversation_state == 3:
                type_of_post = db.read_data_pending(chat_id, "type")
                if type_of_post == "OFFER":
                    db.update_data(chat_id, "item_name", user_input)
                    send_message(text=convo.ask_condition, chat_id=chat_id, reply_markup=itemcondition)
                    db.update_state(chat_id, 4)
                elif type_of_post == "REQUEST":
                    db.update_data(chat_id, "item_name", user_input)
                    send_message(text=convo.ask_item_description, chat_id=chat_id, reply_markup=forcereplykb)
                    db.update_state(chat_id, 4)
                else:
                    send_message(text=convo.invalid_response, chat_id=chat_id)  # fail safe measure any
                print(str(db.read_state(chat_id)))
            elif prev_conversation_state == 4:  # updated item name, update condition now
                type_of_post = db.read_data_pending(chat_id, "type")
                if type_of_post == "OFFER":
                    if user_input == "NEW" or user_input == "USED":
                        db.update_data(chat_id, "condition", user_input)  # update condition
                        send_message(text=convo.ask_condition_rating, chat_id=chat_id, reply_markup=forcereplykb)
                        db.update_state(chat_id, 5)
                        print(str(db.read_state(chat_id)))
                    else:
                        send_message(text=convo.invalid_type, chat_id=chat_id)
                else:
                    db.update_data(chat_id, "item_description", user_input)
                    construct_post(chat_id)
                    send_message(text=convo.thank_you, chat_id=chat_id, reply_markup=removekb)
            elif prev_conversation_state == 5:
                db.update_data(chat_id, "cond_rating", user_input)
                construct_post(chat_id)
                send_message(text=convo.thank_you, chat_id=chat_id, reply_markup=removekb)
            else:
                send_message(text=convo.invalid_response, chat_id=chat_id)


def construct_post(chat_id):
    post_details = db.read_post_data(chat_id)
    db.delete_pending_post(chat_id)

    # get compulsory details for fields
    type_of_post = post_details.get("type", None)
    name = post_details.get("name", None)
    username = check_username(post_details.get("username", None))
    item_name = post_details.get("item_name", None)

    if type_of_post == "OFFER":  # OFFER
        condition = post_details.get("condition")
        cond_rating = check_cond_rating(post_details.get("cond_rating"))
        content = "%E2%9C%A8" + quote(type_of_post + "\n"
                                      + "Name: " + name + "\n"
                                      + "Username: " + username + "\n"
                                      + "Item/Process " + item_name + "\n"
                                      + "Condition: " + condition + "; " + cond_rating + "/10")

    elif type_of_post == "REQUEST":  # REQUEST
        item_description = post_details.get("item_description")
        content = "%F0%9F%8C%88" + quote(type_of_post + "\n"
                                         + "Name: " + name + "\n"
                                         + "Username: " + username + "\n"
                                         + "Item/Process: " + item_name + "\n"
                                         + "Description: " + item_description)
    else:
        send_message(text=convo.invalid_response, chat_id=chat_id)
        content = ""
    print(content)
    uri = "https://api.telegram.org/bot967526375:AAEtE0EXObee7jS-3i7ejXO2NpiG9piHQr4/sendMessage?chat_id" \
          "=@trybetest&text=%s" % content
    urlopen(uri)

    db.add_history_entry("false", chat_id)


def check_username(username):
    if username[0] != "@":
        return "@" + username
    else:
        return username


def check_cond_rating(cond_rating, chat_id):
    if int(cond_rating) > 10 or int(cond_rating) < 0:
        send_message(text=convo.invalid_response, chat_id=chat_id)
    else:
        return cond_rating


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


def send_message(text, chat_id, reply_markup=None):  # /sendMessage API with text and chat ID
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)


def main():
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)  # keeps checking for the id with one bigger than the prev
        # print(len(updates["result"]))
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            handle_updates(updates)
        time.sleep(0.5)


if __name__ == '__main__':
    main()
