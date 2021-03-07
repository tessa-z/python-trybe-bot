import string
import datetime

from trybebot import (db, convo, kb)

TOKEN = "967526375:AAEtE0EXObee7jS-3i7ejXO2NpiG9piHQr4"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)


def handle_check_post(chat_id, user_input, context):
    prev_conversation_state = db.read_state(chat_id)
    if prev_conversation_state == 0:
        db.update_state(chat_id, 1)
        is_expired = db.read_data_history(user_input.text, "expired")
        if is_expired is not None:
            if is_expired == "false":
                context.bot.send_message(text=convo.check_post_not_expired, chat_id=chat_id)
                context.bot.send_message(text=convo.check_post_getusername, chat_id=chat_id,
                                         reply_markup=kb.usernameget)
                db.update_data(chat_id, "inquiring", user_input.text)
            elif is_expired == "true":
                context.bot.send_message(text=convo.check_post_expired, chat_id=chat_id)
            else:
                context.bot.send_message(text=convo.system_error, chat_id=chat_id)
        else:
            context.bot.send_message(text=convo.post_not_found, chat_id=chat_id)
    elif prev_conversation_state == 1:
        if user_input.text == "Sure!":
            post_id = int(db.read_data_pending(chat_id, "inquiring"))
            post_owner_id = str(db.read_data_history(post_id, "chat_id"))
            owner_username_id = context.bot.get_chat(chat_id=post_owner_id).username
            context.bot.send_message(text=convo.check_post_sendusername + owner_username_id, chat_id=chat_id,
                                     reply_markup=kb.removekb)
        elif user_input.text == "Maybe later":
            context.bot.send_message(text=convo.check_post_nogetusername, chat_id=chat_id, reply_markup=kb.removekb)
        else:
            context.bot.send_message(text=convo.invalid_options, chat_id=chat_id, reply_markup=kb.removekb)
        db.delete_from_node(chat_id, "post_pending")
    else:
        context.bot.send_message(text=convo.system_error, chat_id=chat_id, reply_markup=kb.removekb)
        db.delete_from_node(chat_id, "post_pending")


def handle_mark_post(chat_id, user_input, context):
    prev_conversation_state = db.read_state(chat_id)
    if prev_conversation_state == 0:
        # check if the person is the owner of the post, otherwise not authorised
        if is_integer(user_input.text):
            owner_id = db.read_data_history(user_input.text, "chat_id")
            if chat_id == owner_id:
                if is_integer(user_input.text):
                    db.update_history_mark_expired(user_input.text)
                    context.bot.send_message(text=convo.mark_post_success, chat_id=chat_id)
                    db.delete_from_node(chat_id, "post_pending")
                else:
                    context.bot.send_message(text=convo.invalid_number, chat_id=chat_id)
            else:
                if owner_id is None:
                    context.bot.send_message(text=convo.post_not_found, chat_id=chat_id)
                    context.bot.send_message(text=convo.appendix_message, chat_id=chat_id)
                else:
                    context.bot.send_message(text=convo.unauthorised_edit, chat_id=chat_id)
                    context.bot.send_message(text=convo.appendix_message, chat_id=chat_id)
        else:
            context.bot.send_message(text=convo.invalid_number, chat_id=chat_id)
    else:
        context.bot.send_message(text=convo.system_error, chat_id=chat_id)


def handle_create_post(chat_id, user_input, context):
    prev_conversation_state = db.read_state(chat_id)
    if prev_conversation_state == 0:
        context.bot.send_message(text=convo.ask_username_0, chat_id=chat_id, reply_markup=kb.usernameget)
        context.bot.send_message(text=convo.ask_username_1, chat_id=chat_id, reply_markup=kb.usernameget)
        db.update_data(chat_id, "name", user_input.text)
        db.update_state(chat_id, 1)
        print(str(db.read_state(chat_id)))
    elif prev_conversation_state == 1:
        if user_input.text == "Sure!":
            username_id = context.bot.get_chat(chat_id=chat_id).username
            if username_id is not None:
                context.bot.send_message(text=convo.ask_type, chat_id=chat_id, reply_markup=kb.options)
                db.update_data(chat_id, "chat_id", chat_id)
                db.update_state(chat_id, 2)
            else:
                context.bot.send_message(text=convo.ask_username_missing_0, chat_id=chat_id, reply_markup=kb.removekb)
                context.bot.send_message(text=convo.ask_username_missing_1, chat_id=chat_id)
                context.bot.send_message(text=convo.ask_username_missing_2, chat_id=chat_id)
                db.delete_from_node(chat_id, "post_pending")
            print(str(db.read_state(chat_id)))
        elif user_input.text == "Maybe later":
            context.bot.send_message(text=convo.ask_username_rejected_0, chat_id=chat_id, reply_markup=kb.removekb)
            context.bot.send_message(text=convo.ask_username_rejected_1, chat_id=chat_id, reply_markup=kb.removekb)
            context.bot.send_message(text=convo.process_terminated, chat_id=chat_id)
            db.delete_from_node(chat_id, "post_pending")
        else:
            context.bot.send_message(text=convo.invalid_options, chat_id=chat_id)
    elif prev_conversation_state == 2:
        # ask category
        if user_input.text == "Offer":
            context.bot.send_message(text=convo.ask_offer_category, chat_id=chat_id, reply_markup=kb.category)
            db.update_data(chat_id, "type", user_input.text)
            db.update_state(chat_id, 3)
        elif user_input.text == "Request":
            context.bot.send_message(text=convo.ask_request_category, chat_id=chat_id, reply_markup=kb.category)
            db.update_data(chat_id, "type", user_input.text)
            db.update_state(chat_id, 3)
        else:
            context.bot.send_message(text=convo.invalid_options, chat_id=chat_id)
        print(str(db.read_state(chat_id)))
    elif prev_conversation_state == 3:
        # check if within the categories
        if user_input.text in ['Apparel', 'Books/Stationery', 'Electronics', 'Furniture/Appliances',
                               'Toys/Games', 'Others']:
            type_of_post = db.read_data_pending(chat_id, "type")
            if type_of_post == "Offer":
                context.bot.send_message(text=convo.ask_offer_item_name, chat_id=chat_id, reply_markup=kb.forcereplykb)
                db.update_data(chat_id, "item_category", user_input.text)
                db.update_state(chat_id, 4)
            elif type_of_post == "Request":
                context.bot.send_message(text=convo.ask_request_item_name, chat_id=chat_id,
                                         reply_markup=kb.forcereplykb)
                db.update_data(chat_id, "item_category", user_input.text)
                db.update_state(chat_id, 4)
        else:
            context.bot.send_message(text=convo.invalid_options, chat_id=chat_id)
        print(str(db.read_state(chat_id)))
    elif prev_conversation_state == 4:
        type_of_post = db.read_data_pending(chat_id, "type")
        if type_of_post == "Offer":
            context.bot.send_message(text=convo.ask_condition, chat_id=chat_id, reply_markup=kb.itemcondition)
            db.update_data(chat_id, "item_name", user_input.text)
            db.update_state(chat_id, 5)
        elif type_of_post == "Request":
            context.bot.send_message(text=convo.ask_item_description_0, chat_id=chat_id)
            context.bot.send_message(text=convo.ask_item_description_1, chat_id=chat_id, reply_markup=kb.forcereplykb)
            db.update_data(chat_id, "item_name", user_input.text)
            db.update_state(chat_id, 5)
        else:
            context.bot.send_message(text=convo.invalid_response, chat_id=chat_id)
        print(str(db.read_state(chat_id)))
    elif prev_conversation_state == 5:  # updated item name, update condition now
        type_of_post = db.read_data_pending(chat_id, "type")
        if type_of_post == "Offer":
            if user_input.text == "New" or user_input.text == "Used":
                context.bot.send_message(text=convo.ask_condition_rating, chat_id=chat_id, reply_markup=kb.forcereplykb)
                db.update_data(chat_id, "condition", user_input.text)  # update condition
                db.update_state(chat_id, 6)
                print(str(db.read_state(chat_id)))
            else:
                context.bot.send_message(text=convo.invalid_options, chat_id=chat_id)
        elif type_of_post == "Request":
            # check if satisfies length requirements
            if len(user_input.text) > 100:
                context.bot.send_message(text=convo.invalid_desc_length_0, chat_id=chat_id)
                context.bot.send_message(text=convo.invalid_desc_length_1, chat_id=chat_id)
            else:
                db.update_data(chat_id, "item_description", user_input.text)
                db.update_state(chat_id, 8)
                preview_content = construct_post(chat_id, context)
                context.bot.send_message(text=convo.ask_preview_0, chat_id=chat_id)
                context.bot.send_message(text=preview_content, chat_id=chat_id)
                context.bot.send_message(text=convo.ask_preview_1, chat_id=chat_id, reply_markup=kb.preview)
        else:
            context.bot.send_message(text=convo.invalid_response, chat_id=chat_id)
    elif prev_conversation_state == 6:
        # would you like to provide a picture of your item?
        if check_cond_rating(user_input.text):
            db.update_data(chat_id, "cond_rating", user_input.text)
            db.update_state(chat_id, 7)
            context.bot.send_message(text=convo.ask_offer_photo_0, chat_id=chat_id)
            context.bot.send_message(text=convo.ask_offer_photo_1, chat_id=chat_id, reply_markup=kb.skip)
        else:
            context.bot.send_message(text=convo.invalid_range, chat_id=chat_id)
    elif prev_conversation_state == 7:
        if user_input.photo:
            photo_id = user_input.photo[1].file_id
            db.update_data(chat_id, "photo_id", photo_id)
            db.update_state(chat_id, 8)
            preview_content = construct_post(chat_id, context)
            context.bot.send_message(text=convo.ask_preview_0, chat_id=chat_id)
            context.bot.send_photo(caption=preview_content, chat_id=chat_id, photo=photo_id)
            context.bot.send_message(text=convo.ask_preview_1, chat_id=chat_id, reply_markup=kb.preview)
        elif user_input.text == "Skip":
            db.update_state(chat_id, 8)
            preview_content = construct_post(chat_id, context)
            context.bot.send_message(text=convo.ask_preview_0, chat_id=chat_id)
            context.bot.send_message(text=preview_content, chat_id=chat_id)
            context.bot.send_message(text=convo.ask_preview_1, chat_id=chat_id, reply_markup=kb.preview)
        else:
            context.bot.send_message(text=convo.invalid_photo, chat_id=chat_id)
    elif prev_conversation_state == 8:
        if user_input.text == "Yes, send to moderators!":
            context.bot.send_message(text=convo.thank_you, chat_id=chat_id, reply_markup=kb.removekb)
            # update mod db
            epoch_submitted = str(round(datetime.datetime.now().timestamp() * 1000))
            db.transfer_post_data(chat_id, "post_pending", "mod_pending", epoch_submitted)
            db.delete_from_node(chat_id, "post_pending")
        elif user_input.text == "Wait, post later!":
            context.bot.send_message(text=convo.ask_preview_cancelled, chat_id=chat_id)
    else:
        context.bot.send_message(text=convo.invalid_response, chat_id=chat_id)
        db.delete_from_node(chat_id, "post_pending")


def get_photo_id(chat_id):
    post_details = db.read_post_data(chat_id)

    return post_details.get("photo_id")


def construct_post(chat_id, context):
    post_details = db.read_post_data(chat_id)

    # get compulsory details for fields
    type_of_post = str(post_details.get("type", None))
    name = string.capwords(post_details.get("name", None))
    item_category = "#" + str(post_details.get("item_category", None)).lower()
    item_name = str(post_details.get("item_name", None)).capitalize()
    post_id = " #" + str(db.read_latest_index())

    if type_of_post == "Offer":  # Offer
        condition = post_details.get("condition")
        cond_rating = post_details.get("cond_rating")
        content = "✨" + type_of_post + post_id + "\n" \
                  + "Name: " + name + "\n" \
                  + "Category: " + item_category + "\n" \
                  + "Item/Process: " + item_name + "\n" \
                  + "Condition: " + condition + "; " + cond_rating + "/10"

    elif type_of_post == "Request":  # Request
        item_description = post_details.get("item_description").capitalize()
        content = "🌈" + type_of_post + post_id + "\n" \
                  + "Name: " + name + "\n" \
                  + "Category:" + item_category + "\n" \
                  + "Item/Process: " + item_name + "\n" \
                  + "Description: " + item_description
    else:
        context.bot.send_message(text=convo.invalid_response, chat_id=chat_id)
        content = ""
    return content


def check_cond_rating(cond_rating):
    try:
        is_integer(cond_rating)
        if int(cond_rating) > 10 or int(cond_rating) < 0:
            return False
        else:
            return True
    except ValueError:
        return False


def is_integer(num):
    try:
        if int(num):
            return True
        else:
            return False
    except ValueError:
        return False
