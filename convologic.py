import string

from urllib.request import urlopen
from urllib.parse import quote
from trybebot import (db, convo, kb, comms)


TOKEN = "967526375:AAEtE0EXObee7jS-3i7ejXO2NpiG9piHQr4"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)


def handle_check_post(chat_id, user_input):
    prev_conversation_state = db.read_state(chat_id)
    db.delete_pending_activity(chat_id)
    if prev_conversation_state == 0:
        is_expired = db.read_data_history(user_input, "expired")
        if is_expired is not None:
            if is_expired == "false":
                comms.send_message(text=convo.check_post_not_expired, chat_id=chat_id)
            elif is_expired == "true":
                comms.send_message(text=convo.check_post_expired, chat_id=chat_id)
            else:
                comms.send_message(text=convo.system_error, chat_id=chat_id)
        else:
            comms.send_message(text=convo.post_not_found, chat_id=chat_id)
    else:
        comms.send_message(text=convo.system_error, chat_id=chat_id)


def handle_mark_post(chat_id, user_input):
    prev_conversation_state = db.read_state(chat_id)
    db.delete_pending_activity(chat_id)
    if prev_conversation_state == 0:
        # check if the person is the owner of the post, otherwise not authorised
        owner_id = db.read_data_history(user_input, "chat_id")
        if chat_id == owner_id:
            db.update_history_mark_expired(user_input)
            comms.send_message(text=convo.mark_post_success, chat_id=chat_id)
        else:
            if owner_id is None:
                comms.send_message(text=convo.post_not_found, chat_id=chat_id)
            else:
                comms.send_message(text=convo.unauthorised_edit, chat_id=chat_id)
    else:
        comms.send_message(text=convo.system_error, chat_id=chat_id)


def handle_create_post(chat_id, user_input):
    prev_conversation_state = db.read_state(chat_id)
    if prev_conversation_state == 0:
        db.update_data(chat_id, "name", user_input)
        comms.send_message(text=convo.ask_username, chat_id=chat_id, reply_markup=kb.forcereplykb)
        db.update_state(chat_id, 1)
        print(str(db.read_state(chat_id)))
    elif prev_conversation_state == 1:
        db.update_data(chat_id, "username", user_input)
        comms.send_message(text=convo.ask_type, chat_id=chat_id, reply_markup=kb.options)
        db.update_state(chat_id, 2)
        print(str(db.read_state(chat_id)))
    elif prev_conversation_state == 2:
        if user_input == "OFFER":
            db.update_data(chat_id, "type", user_input)
            comms.send_message(text=convo.ask_offer_item_name, chat_id=chat_id, reply_markup=kb.forcereplykb)
            db.update_state(chat_id, 3)
        elif user_input == "REQUEST":
            db.update_data(chat_id, "type", user_input)
            comms.send_message(text=convo.ask_request_item_name, chat_id=chat_id, reply_markup=kb.forcereplykb)
            db.update_state(chat_id, 3)
        else:
            comms.send_message(text=convo.invalid_options, chat_id=chat_id)  # fail safe measure any
        print(str(db.read_state(chat_id)))
    elif prev_conversation_state == 3:
        type_of_post = db.read_data_pending(chat_id, "type")
        if type_of_post == "OFFER":
            db.update_data(chat_id, "item_name", user_input)
            comms.send_message(text=convo.ask_condition, chat_id=chat_id, reply_markup=kb.itemcondition)
            db.update_state(chat_id, 4)
        elif type_of_post == "REQUEST":
            db.update_data(chat_id, "item_name", user_input)
            comms.send_message(text=convo.ask_item_description, chat_id=chat_id, reply_markup=kb.forcereplykb)
            db.update_state(chat_id, 4)
        else:
            comms.send_message(text=convo.invalid_response, chat_id=chat_id)  # fail safe measure any
        print(str(db.read_state(chat_id)))
    elif prev_conversation_state == 4:  # updated item name, update condition now
        type_of_post = db.read_data_pending(chat_id, "type")
        if type_of_post == "OFFER":
            if user_input == "NEW" or user_input == "USED":
                db.update_data(chat_id, "condition", user_input)  # update condition
                comms.send_message(text=convo.ask_condition_rating, chat_id=chat_id, reply_markup=kb.forcereplykb)
                db.update_state(chat_id, 5)
                print(str(db.read_state(chat_id)))
            else:
                comms.send_message(text=convo.invalid_options, chat_id=chat_id)
        else:
            db.update_data(chat_id, "item_description", user_input)
            construct_post(chat_id)
            comms.send_message(text=convo.thank_you, chat_id=chat_id, reply_markup=kb.removekb)
    elif prev_conversation_state == 5:
        if check_cond_rating(user_input, chat_id):
            db.update_data(chat_id, "cond_rating", user_input)
            construct_post(chat_id)
            comms.send_message(text=convo.thank_you, chat_id=chat_id, reply_markup=kb.removekb)
        else:
            comms.send_message(text=convo.invalid_range, chat_id=chat_id)
    else:
        comms.send_message(text=convo.invalid_response, chat_id=chat_id)


def construct_post(chat_id):
    post_details = db.read_post_data(chat_id)
    db.delete_pending_activity(chat_id)

    # get compulsory details for fields
    type_of_post = post_details.get("type", None)
    name = string.capwords(post_details.get("name", None))
    username = check_username(post_details.get("username", None))
    item_name = post_details.get("item_name", None).capitalize()
    post_id = " #" + str(db.read_latest_index())

    if type_of_post == "OFFER":  # OFFER
        condition = post_details.get("condition")
        cond_rating = post_details.get("cond_rating")
        content = "%E2%9C%A8" + quote(type_of_post + post_id + "\n"
                                      + "Name: " + name + "\n"
                                      + "Username: " + username + "\n"
                                      + "Item/Process: " + item_name + "\n"
                                      + "Condition: " + condition + "; " + cond_rating + "/10")

    elif type_of_post == "REQUEST":  # REQUEST
        item_description = post_details.get("item_description").capitalize()
        content = "%F0%9F%8C%88" + quote(type_of_post + post_id + "\n"
                                         + "Name: " + name + "\n"
                                         + "Username: " + username + "\n"
                                         + "Item/Process: " + item_name + "\n"
                                         + "Description: " + item_description)
    else:
        comms.send_message(text=convo.invalid_response, chat_id=chat_id)
        content = ""
    print(content)
    uri = "https://api.telegram.org/bot967526375:AAEtE0EXObee7jS-3i7ejXO2NpiG9piHQr4/sendMessage?chat_id" \
          "=@ruaok&text=%s" % content
    urlopen(uri)

    db.add_history_entry("false", chat_id)


def check_username(username):
    if username[0] != "@":
        return "@" + username.lower()
    else:
        return username.lower()


def check_cond_rating(cond_rating, chat_id):
    if int(cond_rating) > 10 or int(cond_rating) < 0:
        return False
    else:
        return True
