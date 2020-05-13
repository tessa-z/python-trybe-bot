#!/usr/bin/env python3

import sqlite3


class DBHelper:
    def __init__(self, dbname="trybeusers.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)  # creates db connection

    def setup(self):
        tblstmt = "CREATE TABLE IF NOT EXISTS users (name text, username text, type text, itemName text, condition " \
                  "text, conditionDesc text, owner text, state int, current int) "
        # ownidx = "CREATE INDEX IF NOT EXISTS ownIndex ON users (owner ASC)"
        self.conn.execute(tblstmt)
        # self.conn.execute(ownidx)
        self.conn.commit()

    def update_field(self, state, owner, update_text=""):  # depending on state, update relevant field
        # state definitions
        INITIALISE_ENTRY = 0
        UPDATE_NAME = 1
        UPDATE_USERNAME = 2
        UPDATE_OFFER_REQUEST = 3
        UPDATE_ITEM_NAME = 4
        UPDATE_CONDITION_DESC = 5
        UPDATE_CONDITION_NUMBER = 6

        if state == INITIALISE_ENTRY:  # record chat_id
            stmt = "INSERT INTO users VALUES (?,?,?,?,?,?,?,?,?)"
            args = ('-', '-', '-', '-', '-', '-', owner, 0, 100)
            self.conn.execute(stmt, args)
            self.conn.commit()

        elif state == UPDATE_NAME:  # input name
            stmt = "UPDATE users SET name = (?), state = (?) WHERE owner = (?) AND state <100"
            args = (update_text, 1, owner)
            self.conn.execute(stmt, args)
            self.conn.commit()

        elif state == UPDATE_USERNAME:  # input username
            stmt = "UPDATE users SET username = (?), state = (?) WHERE owner = (?) AND state <100"
            if update_text[0] != "@":
                update_text = "@" + update_text
            args = (update_text, 2, owner)
            self.conn.execute(stmt, args)
            self.conn.commit()

        elif state == UPDATE_OFFER_REQUEST:  # OFFER or REQUEST
            stmt = "UPDATE users SET type = (?), state = (?) WHERE owner = (?) AND state <100"
            args = (update_text, 3, owner)
            self.conn.execute(stmt, args)
            self.conn.commit()

        elif state == UPDATE_ITEM_NAME:  # item name
            stmt = "UPDATE users SET itemName = (?), state = (?) WHERE owner = (?) AND state <100"
            args = (update_text, 4, owner)
            self.conn.execute(stmt, args)
            self.conn.commit()

        elif state == UPDATE_CONDITION_DESC:  # condition out of 10 or description
            stmt = "UPDATE users SET conditionDesc = (?), state = (?) WHERE owner = (?) AND state <100"
            args = (update_text, 100, owner)  # database does not update state to 100
            self.conn.execute(stmt, args)
            self.conn.commit()

        elif state == UPDATE_CONDITION_NUMBER:
            stmt = "UPDATE users SET condition = (?), state = (?) WHERE owner = (?) AND state <100"
            args = (update_text, 5, owner)
            self.conn.execute(stmt, args)
            self.conn.commit()

    def read_state(self, owner):  # must not return an array or everything be screwed my friend
        stmt = "SELECT * FROM users WHERE owner = (?) AND state <100"
        args = (owner,)
        return [x[7] for x in self.conn.execute(stmt, args)]  # x is a tuple in the form ("string", )

    def update_state(self, new_state, owner, original_state):  # set the state value to the number indicated in param
        stmt = "UPDATE users SET state = (?) WHERE owner = (?) AND state = (?)"
        args = (new_state, owner, original_state)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def read_type(self, owner):
        stmt = "SELECT * FROM users WHERE owner = (?) AND state >= 0 AND state <100"
        args = (owner,)
        return [x[2] for x in self.conn.execute(stmt, args)]  # x is a tuple in the form ("string", )

    def add_field(self, item_text, owner):
        stmt = "INSERT INTO users (description, owner) VALUES (?, ?)"
        args = (item_text, owner)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_user(self, owner):
        stmt = "DELETE FROM users WHERE owner = (?)"
        args = (owner,)
        self.conn.execute(stmt, args)
        self.conn.commit()

    # def get_items(self, owner):
    #     stmt = "SELECT name, username, type, field1, field2 FROM users WHERE owner = (?)"
    #     args = (owner, )
    #     x = self.conn.execute(stmt, args)
    #     arr = [x[0], x[1], x[2], x[3], x[4]]
    #     return arr #x is a tuple in the form ("string", )
    #     # return [x[0] for x in self.conn.execute(stmt, args)] #x is a tuple in the form ("string", )

    def get_details(self, owner, index):
        stmt = "SELECT name, username, type, itemName, condition, conditionDesc FROM users WHERE owner = (?) AND state == 100"
        args = (owner,)
        return [x[index] for x in self.conn.execute(stmt, args)]  # x is a tuple in the form ("string",
