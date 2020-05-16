#!/usr/bin/env python3
import logging
import time  # to enable timeout
import random

from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters

import messages
import database
import convologic
import keyboard
import comms

convo = messages.Messages()
db = database.FirebaseHelper()
kb = keyboard.KeyBoard()

updater = Updater(token='967526375:AAEtE0EXObee7jS-3i7ejXO2NpiG9piHQr4', use_context=True)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s = %(message)s', level=logging.INFO)


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=convo.welcome)


def cancel(update, context):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text=convo.process_terminated)
    db.update_state(chat_id, 0)  # reset the state to 0
    db.delete_pending_activity(chat_id)
    print(str(db.read_state(chat_id)))


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=convo.invalid_command)


def create_post(update, context):
    chat_id = update.effective_chat.id
    user_input = update.message.text
    context.bot.send_message(chat_id=chat_id, text=convo.ask_name, reply_markup=kb.forcereplykb)
    db.update_state(chat_id, 0)
    db.update_data(chat_id, "command", user_input)


def chat(update, context):
    chat_id = update.effective_chat.id
    user_input = update.message.text
    current_command = db.read_data_pending(chat_id, "command")
    if current_command == "/checkpost":
        convologic.handle_check_post(chat_id, user_input, context)
    elif current_command == "/markpost":
        convologic.handle_mark_post(chat_id, user_input, context)
    elif current_command == "/createpost":
        convologic.handle_create_post(chat_id, user_input, context)
    else:
        context.bot.send_message(chat_id=chat_id, text=convo.unknown_text)


def check_post(update, context):
    chat_id = update.effective_chat.id
    user_input = update.message.text
    context.bot.send_message(chat_id=chat_id, text=convo.check_post, reply_markup=kb.forcereplykb)
    db.update_data(chat_id, "command", user_input)
    db.update_data(chat_id, "state", 0)


def mark_post(update, context):
    chat_id = update.effective_chat.id
    user_input = update.message.text
    context.bot.send_message(chat_id=chat_id, text=convo.mark_post, reply_markup=kb.forcereplykb)
    db.update_data(chat_id, "command", user_input)
    db.update_data(chat_id, "state", 0)


def sticker(update, context):
    sticker_set = context.bot.get_sticker_set(update.message.sticker.set_name)
    random_sticker_id = get_random_sticker_id(sticker_set)
    context.bot.send_sticker(chat_id=update.effective_chat.id, sticker=random_sticker_id)


def get_random_sticker_id(sticker_set):
    sticker_list = sticker_set.stickers
    random_sticker_index = random.randint(0, len(sticker_list)-1)
    random_sticker_id = str(sticker_list[random_sticker_index].file_id)
    return random_sticker_id


def handle_updates(updates):
    # print(updates)
    for update in updates["result"]:
        chat_id = update["message"]["chat"]["id"]
        try:
            user_input = update["message"]["text"]
        except Exception:
            comms.send_message(text=convo.invalid_response, chat_id=chat_id)

        if user_input == "/start":
            comms.send_message(text=convo.welcome, chat_id=chat_id)
        elif user_input == "/cancel":
            comms.send_message(text=convo.process_terminated, chat_id=chat_id, reply_markup=kb.removekb)
            db.update_state(chat_id, 0)  # reset the state to 0
            db.delete_pending_activity(chat_id)
            print(str(db.read_state(chat_id)))
        elif user_input == "/createpost":
            db.update_state(chat_id, 0)
            db.update_data(chat_id, "command", user_input)
            comms.send_message(text=convo.ask_name, chat_id=chat_id, reply_markup=kb.forcereplykb)
            print(str(db.read_state(chat_id)))
        elif user_input == "/checkpost":
            # must check that users are not in the middle of constructing a post
            db.update_data(chat_id, "command", user_input)
            db.update_data(chat_id, "state", 0)
            comms.send_message(text=convo.check_post, chat_id=chat_id, reply_markup=kb.forcereplykb)
        elif user_input == "/markpost":
            db.update_data(chat_id, "command", user_input)
            db.update_data(chat_id, "state", 0)
            comms.send_message(text=convo.mark_post, chat_id=chat_id, reply_markup=kb.forcereplykb)
        elif user_input.startswith("/"):
            comms.send_message(text=convo.invalid_command, chat_id=chat_id, reply_markup=kb.removekb)
            continue
        else:
            current_command = db.read_data_pending(chat_id, "command")
            if current_command == "/checkpost":
                convologic.handle_check_post(chat_id, user_input)
            elif current_command == "/markpost":
                convologic.handle_mark_post(chat_id, user_input)
            elif current_command == "/createpost":
                convologic.handle_create_post(chat_id, user_input)
            else:
                comms.send_message(text=convo.unknown_text, chat_id=chat_id)


def setup_handlers():
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    cancel_handler = CommandHandler('cancel', cancel)
    dispatcher.add_handler(cancel_handler)

    create_post_handler = CommandHandler('createpost', create_post)
    dispatcher.add_handler(create_post_handler)

    check_post_handler = CommandHandler('checkpost', check_post)
    dispatcher.add_handler(check_post_handler)

    mark_post_handler = CommandHandler('markpost', mark_post)
    dispatcher.add_handler(mark_post_handler)

    chat_handler = MessageHandler(Filters.text & (~Filters.command), chat)
    dispatcher.add_handler(chat_handler)

    sticker_handler = MessageHandler(Filters.sticker, sticker)
    dispatcher.add_handler(sticker_handler)

    # put this last or other commands would be skipped!
    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)


def main():
    last_update_id = None
    while True:
        updates = comms.get_updates(last_update_id)  # keeps checking for the id with one bigger than the prev
        # print(len(updates["result"]))
        print(updates)
        if len(updates["result"]) > 0:
            last_update_id = comms.get_last_update_id(updates) + 1
            handle_updates(updates)
        time.sleep(0.5)


if __name__ == '__main__':
    # main()
    setup_handlers()
    updater.start_polling()
    updater.idle()
