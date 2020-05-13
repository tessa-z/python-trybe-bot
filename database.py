import pyrebase
from collections import OrderedDict

config = {
    "apiKey": "AIzaSyCuzOK3YTeM5GhZqSIdLBbbFDTVlPcv8d4",
    "authDomain": "python-trybe-bot.firebaseapp.com",
    "databaseURL": "https://python-trybe-bot.firebaseio.com/",
    "storageBucket": "python-trybe-bot.appspot.com"
}

firebase = pyrebase.initialize_app(config)

# Get a reference to the database service
db = firebase.database()


def read_state(owner):
    state_details = db.child("post_pending").child(owner).child("state").get().val()
    return state_details


def read_data(owner, key):
    data_value = db.child("post_pending").child(owner).child(key).get().val()
    return data_value


def update_latest_index():
    old_index = db.child("latest_index").get().val()
    new_index = str(int(old_index) + 1).zfill(5)
    db.child("latest_index").set(new_index)


def update_history(index, expired, username):
    history_data = {"expired": expired, "username": username}
    db.child("post_history").child(index).set(history_data)


def update_data(owner, key, value):
    pending_data = {key: value}
    db.child("post_pending").child(owner).update(pending_data)


def update_state(owner, state):
    state_data = {"state": state}
    db.child("post_pending").child(owner).update(state_data)


def delete_pending_post(owner):
    db.child("post_pending").child(owner).child("item_name").remove()


def get_post_data(owner):
    post_details = db.child("post_pending").child(owner).get().val()
    return post_details


if __name__ == '__main__':
    # update_latest_index()
    # update_history("00002", "false", "tessa_z")
    update_data("557099000", "item_name", "fishies")
    update_data("557099000", "state", 0)
    update_data("557099000", "name", "Catto")
    # print(read_state("557099000"))
    # delete_pending_post("557099000")
    print(get_post_data("557099000"))
    print(type(get_post_data("557099000").get("item_name", None)))
