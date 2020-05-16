import pyrebase

config = {
    "apiKey": "AIzaSyCuzOK3YTeM5GhZqSIdLBbbFDTVlPcv8d4",
    "authDomain": "python-trybe-bot.firebaseapp.com",
    "databaseURL": "https://python-trybe-bot.firebaseio.com/",
    "storageBucket": "python-trybe-bot.appspot.com"
}


class FirebaseHelper:

    def __init__(self):
        firebase = pyrebase.initialize_app(config)
        # Get a reference to the database service
        self.db = firebase.database()

    def read_state(self, owner):
        state_details = self.db.child("post_pending").child(owner).child("state").get().val()
        return state_details

    def read_data_pending(self, owner, key):
        data_value = self.db.child("post_pending").child(owner).child(key).get().val()
        return data_value

    def read_data_history(self, post_index, key):
        history_data = self.db.child("post_history").child(post_index).child(key).get().val()
        return history_data

    def update_latest_index(self):
        new_index = self.read_latest_index() + 1
        self.db.child("latest_index").set(new_index)

    def read_latest_index(self):
        latest_index = self.db.child("latest_index").get().val()
        return latest_index

    def add_history_entry(self, expired, username, chat_id):
        history_data = {"expired": expired, "username": username, "chat_id": chat_id}
        latest_index = self.read_latest_index()
        self.db.child("post_history").child(latest_index).set(history_data)
        self.update_latest_index()

    def update_history_mark_expired(self, post_index):
        history_data = {"expired": "true"}
        self.db.child("post_history").child(post_index).update(history_data)

    def update_data(self, owner, key, value):
        pending_data = {key: value}
        self.db.child("post_pending").child(owner).update(pending_data)

    def update_state(self, owner, state):
        state_data = {"state": state}
        self.db.child("post_pending").child(owner).update(state_data)

    def delete_pending_activity(self, owner):
        self.db.child("post_pending").child(owner).remove()

    def read_post_data(self, owner):
        post_details = self.db.child("post_pending").child(owner).get().val()
        return post_details
