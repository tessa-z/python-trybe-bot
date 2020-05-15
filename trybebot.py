#!/usr/bin/env python3

import time  # to enable timeout
import messages
import database
import convologic
import keyboard
import comms

convo = messages.Messages()
db = database.FirebaseHelper()
kb = keyboard.KeyBoard()

updater = Updater(token="1179717191:AAG2EeROiLFFBqYQ3ofq1ltDQM1zU3ZIETI", use_context=True)
dispatcher = updater.dispatcher


def handle_updates(updates):
    # print(updates)
    for update in updates["result"]:
        user_input = update["message"]["text"]
        chat_id = update["message"]["chat"]["id"]

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


def main():
    last_update_id = None
    while True:
        updates = comms.get_updates(last_update_id)  # keeps checking for the id with one bigger than the prev
        # print(len(updates["result"]))
        if len(updates["result"]) > 0:
            last_update_id = comms.get_last_update_id(updates) + 1
            handle_updates(updates)
        time.sleep(0.5)


if __name__ == '__main__':
    main()
