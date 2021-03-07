#!/usr/bin/env python3
import logging
import os
import random

from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters

import messages
import fbhelper
import convologic
import keyboard

convo = messages.Messages()
db = fbhelper.FirebaseHelper()
kb = keyboard.KeyBoard()

updater = Updater(token='967526375:AAEtE0EXObee7jS-3i7ejXO2NpiG9piHQr4', use_context=True)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s = %(message)s', level=logging.INFO)


def start_(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=convo.welcome)


def help_(update, context):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text=convo.help)
    db.delete_from_node(chat_id, "post_pending")


def cancel_(update, context):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text=convo.process_terminated)
    db.delete_from_node(chat_id, "post_pending")


def unknown_(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=convo.invalid_command)


def create_post(update, context):
    chat_id = update.effective_chat.id
    user_input = update.message.text
    context.bot.send_message(chat_id=chat_id, text=convo.ask_name, reply_markup=kb.forcereplykb)
    db.update_state(chat_id, 0)
    db.update_data(chat_id, "command", user_input)


def chat_(update, context):
    chat_id = update.effective_chat.id
    user_input = update.message
    current_command = db.read_data_pending(chat_id, "command")

    if current_command == "/checkpost":
        convologic.handle_check_post(chat_id, user_input, context)
    elif current_command == "/markpost":
        convologic.handle_mark_post(chat_id, user_input, context)
    elif current_command == "/createpost":
        convologic.handle_create_post(chat_id, user_input, context)
    else:
        if update.effective_chat.id > 0:
            # update is from user account
            context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)
        else:
            print(update)


def check_post(update, context):
    chat_id = update.effective_chat.id
    user_input = update.message.text
    context.bot.send_message(chat_id=chat_id, text=convo.check_post_0, reply_markup=kb.forcereplykb)
    context.bot.send_message(chat_id=chat_id, text=convo.check_post_1, reply_markup=kb.forcereplykb)
    db.update_data(chat_id, "command", user_input)
    db.update_data(chat_id, "state", 0)


def mark_post(update, context):
    chat_id = update.effective_chat.id
    user_input = update.message.text
    context.bot.send_message(chat_id=chat_id, text=convo.mark_post_0, reply_markup=kb.forcereplykb)
    context.bot.send_message(chat_id=chat_id, text=convo.mark_post_1, reply_markup=kb.forcereplykb)
    db.update_data(chat_id, "command", user_input)
    db.update_data(chat_id, "state", 0)


def contact_mod(update, context):
    chat_id = update.effective_chat.id
    context.bot.send_message(text=convo.contact_us, chat_id=chat_id)


def sticker_(update, context):
    sticker_set = context.bot.get_sticker_set(update.message.sticker.set_name)
    random_sticker_id = get_random_sticker_id(sticker_set)
    context.bot.send_sticker(chat_id=update.effective_chat.id, sticker=random_sticker_id)


def animation_(update, context):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text=convo.gif_seal_0)
    context.bot.send_animation(chat_id=chat_id, animation=convo.gif_seal_id)
    context.bot.send_message(chat_id=chat_id, text=convo.gif_seal_1)


def get_random_sticker_id(sticker_set):
    sticker_list = sticker_set.stickers
    random_sticker_index = random.randint(0, len(sticker_list) - 1)
    random_sticker_id = str(sticker_list[random_sticker_index].file_id)
    return random_sticker_id


def setup_handlers():
    start_handler = CommandHandler('start', start_)
    dispatcher.add_handler(start_handler)

    cancel_handler = CommandHandler('cancel', cancel_)
    dispatcher.add_handler(cancel_handler)

    help_handler = CommandHandler('help', help_)
    dispatcher.add_handler(help_handler)

    create_post_handler = CommandHandler('createpost', create_post)
    dispatcher.add_handler(create_post_handler)

    check_post_handler = CommandHandler('checkpost', check_post)
    dispatcher.add_handler(check_post_handler)

    mark_post_handler = CommandHandler('markpost', mark_post)
    dispatcher.add_handler(mark_post_handler)

    contact_mod_handler = CommandHandler('contactmod', contact_mod)
    dispatcher.add_handler(contact_mod_handler)

    chat_handler = MessageHandler(Filters.text & (~Filters.command), chat_)
    dispatcher.add_handler(chat_handler)

    photo_handler = MessageHandler(Filters.photo, chat_)
    dispatcher.add_handler(photo_handler)

    sticker_handler = MessageHandler(Filters.sticker, sticker_)
    dispatcher.add_handler(sticker_handler)

    animation_handler = MessageHandler(Filters.animation, animation_)
    dispatcher.add_handler(animation_handler)

    # put this last or other commands would be skipped!
    unknown_handler = MessageHandler(Filters.command, unknown_)
    dispatcher.add_handler(unknown_handler)


if __name__ == '__main__':
    # main()
    setup_handlers()
    updater.start_polling()
    updater.idle()
