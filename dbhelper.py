#!/usr/bin/env python3

import sqlite3

class DBHelper:
    def __init__(self, dbname="trybeusers.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname) #creates db connection


    def setup(self):
        tblstmt = "CREATE TABLE IF NOT EXISTS users (name text, username text, type text, field1 text, condition text, field2 text, owner text, state int, current int)"
        # ownidx = "CREATE INDEX IF NOT EXISTS ownIndex ON users (owner ASC)"
        self.conn.execute(tblstmt)
        # self.conn.execute(ownidx)
        self.conn.commit()

    def update_field(self, state, owner, update_text=""): #depending on state, update relevant field
        if state == 0: #record chat_id
            stmt = "INSERT INTO users VALUES (?,?,?,?,?,?,?,?,?)"
            args = ('name', 'username', 'type', 'field1', 'NA', 'field2', owner, 0, 100)
            self.conn.execute(stmt, args)
            self.conn.commit()

        elif state == 1: #input name
            stmt = "UPDATE users SET name = (?), state = (?) WHERE owner = (?) AND state <100"
            args = (update_text, 1, owner)
            print("here i am")
            self.conn.execute(stmt, args)
            self.conn.commit()

        elif state == 2: #input username
            stmt = "UPDATE users SET username = (?), state = (?) WHERE owner = (?) AND state <100"
            if update_text[0] != "@":
                update_text = "@" + update_text
            args = (update_text, 2, owner)
            print("here i am 2")
            self.conn.execute(stmt, args)
            self.conn.commit()

        elif state == 3: #OFFER or REQUEST
            stmt = "UPDATE users SET type = (?), state = (?) WHERE owner = (?) AND state <100"
            args = (update_text, 3, owner)
            self.conn.execute(stmt, args)
            self.conn.commit()

        elif state == 4: #field1
            stmt = "UPDATE users SET field1 = (?), state = (?) WHERE owner = (?) AND state <100"
            args = (update_text, 4, owner)
            self.conn.execute(stmt, args)
            self.conn.commit()

        elif state == 5: #field2
            stmt = "UPDATE users SET field2 = (?), state = (?) WHERE owner = (?)"
            args = (update_text, 100, owner)
            self.conn.execute(stmt, args)
            self.conn.commit()

        elif state == 6:
            stmt = "UPDATE users SET condition = (?), state = (?) WHERE owner = (?)"
            args = (update_text, 6, owner)
            self.conn.execute(stmt, args)
            self.conn.commit()

    def read_state(self, owner):
        stmt = "SELECT * FROM users WHERE owner = (?) AND state <100"
        args = (owner, )
        return [x[7] for x in self.conn.execute(stmt, args)] #x is a tuple in the form ("string", )

    def read_type(self, owner):
        stmt = "SELECT * FROM users WHERE owner = (?) AND state >= 0 AND state <100"
        args = (owner, )
        return [x[2] for x in self.conn.execute(stmt, args)] #x is a tuple in the form ("string", )

    def add_field(self, item_text, owner):
        stmt = "INSERT INTO users (description, owner) VALUES (?, ?)"
        args = (item_text, owner)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_user(self, owner):
        stmt = "DELETE FROM users WHERE owner = (?)"
        args = (owner, )
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
        stmt = "SELECT name, username, type, field1, condition, field2 FROM users WHERE owner = (?)"
        args = (owner, )
        return [x[index] for x in self.conn.execute(stmt, args)] #x is a tuple in the form ("string", )
        # return [x[0] for x in self.conn.execute(stmt, args)] #x is a tuple in the form ("string", )
