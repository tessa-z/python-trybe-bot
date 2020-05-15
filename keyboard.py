import json


class KeyBoard:

    def __init__(self):
        self.forcereplykb = self.force_reply()
        self.removekb = self.remove_keyboard()
        self.options = self.build_keyboard()
        self.itemcondition = self.build_keyboard2()  # extract this into a setup function

    def build_keyboard(self):
        keyboard = [['OFFER', 'REQUEST']]
        reply_markup = {"keyboard": keyboard, "resize_keyboard": True, "one_time_keyboard": True}
        return json.dumps(reply_markup)

    def build_keyboard2(self):
        keyboard = [['NEW', 'USED']]
        reply_markup = {"keyboard": keyboard, "resize_keyboard": True, "one_time_keyboard": True}
        return json.dumps(reply_markup)

    def force_reply(self):
        reply_markup = {"force_reply": True, "selective": False}
        return json.dumps(reply_markup)

    def remove_keyboard(self):
        reply_markup = {"remove_keyboard": True}
        return json.dumps(reply_markup)
