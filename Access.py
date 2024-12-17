import sqlite3

def executeCTX(sql,data):
    with sqlite3.connect('ctx.db') as db:
        cursor = db.cursor()
        cursor.execute(sql,data)
        returnable = cursor.fetchall()
        return returnable

def executeCTX2(sql,data):
    with sqlite3.connect('ctx2.db') as db:
        cursor = db.cursor()
        cursor.execute(sql,data)
        returnable = cursor.fetchall()
        return returnable