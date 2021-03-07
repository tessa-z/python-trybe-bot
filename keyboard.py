import json


class KeyBoard:

    def __init__(self):
        self.forcereplykb = self.force_reply()
        self.removekb = self.remove_keyboard()
        self.options = self.build_keyboard1()
        self.category = self.build_keyboard6()
        self.itemcondition = self.build_keyboard2()  # extract this into a setup function
        self.usernameget = self.build_keyboard3()
        self.preview = self.build_keyboard4()
        self.skip = self.build_keyboard5()

    def build_keyboard1(self):
        keyboard = [['Offer', 'Request']]
        reply_markup = {"keyboard": keyboard, "resize_keyboard": True, "one_time_keyboard": True}
        return json.dumps(reply_markup)

    def build_keyboard2(self):
        keyboard = [['New', 'Used']]
        reply_markup = {"keyboard": keyboard, "resize_keyboard": True, "one_time_keyboard": True}
        return json.dumps(reply_markup)

    def build_keyboard3(self):
        keyboard = [['Sure!', 'Maybe later']]
        reply_markup = {"keyboard": keyboard, "resize_keyboard": True, "one_time_keyboard": True}
        return json.dumps(reply_markup)

    def build_keyboard4(self):
        keyboard = [['Yes, send to moderators!', 'Wait, post later!']]
        reply_markup = {"keyboard": keyboard, "resize_keyboard": True, "one_time_keyboard": True}
        return json.dumps(reply_markup)

    def build_keyboard5(self):
        keyboard = [['Skip']]
        reply_markup = {"keyboard": keyboard, "resize_keyboard": True, "one_time_keyboard": True}
        return json.dumps(reply_markup)

    def build_keyboard6(self):
        keyboard = [['Apparel'], ['Books/Stationery'], ['Electronics'],
                    ['Furniture/Appliances'], ['Toys/Games'], ['Others']]
        reply_markup = {"keyboard": keyboard, "resize_keyboard": True, "one_time_keyboard": True}
        return json.dumps(reply_markup)

    def force_reply(self):
        reply_markup = {"force_reply": True, "selective": False}
        return json.dumps(reply_markup)

    def remove_keyboard(self):
        reply_markup = {"remove_keyboard": True}
        return json.dumps(reply_markup)
