import sqlite3
import datetime


def create_db():
    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS m_chat_id(
                rowid INTEGER PRIMARY KEY, m_chat_id INTEGER, fio TEXT, guest_fio TEXT, date TEXT, time TEXT,
                status INTEGER
                )""")
    connect.commit()
    cursor.close()


def get_status(message):
    sqlite_connection = sqlite3.connect('users.db')
    cursor = sqlite_connection.cursor()
    records = ''
    try:
        sqlite_select_query = """SELECT * from m_chat_id where m_chat_id = ? ORDER BY rowid DESC"""
        cursor.execute(sqlite_select_query, [message.chat.id])
        records = cursor.fetchmany(2)
        cursor.close()
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
    return records


def get_all_requests():
    sqlite_connection = sqlite3.connect('users.db')
    cursor = sqlite_connection.cursor()
    records = ''
    try:
        sqlite_select_query = """SELECT * from m_chat_id ORDER BY rowid DESC"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        cursor.close()
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
    return records


def get_today_requests():
    sqlite_connection = sqlite3.connect('users.db')
    cursor = sqlite_connection.cursor()
    records = ''
    try:
        sqlite_select_query = """SELECT * FROM m_chat_id WHERE date = ? ORDER BY time DESC"""
        cursor.execute(sqlite_select_query, (datetime.date.today().strftime("%d.%m.%Y"), ))
        records = cursor.fetchall()
        cursor.close()
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
    return records


def get_actual_requests():
    sqlite_connection = sqlite3.connect('users.db')
    cursor = sqlite_connection.cursor()
    records = ''
    try:
        sqlite_select_query = """SELECT * FROM m_chat_id WHERE date >= ? ORDER BY date ASC"""
        cursor.execute(sqlite_select_query, (datetime.date.today().strftime("%d.%m.%Y"), ))
        records = cursor.fetchall()
        cursor.close()
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
    return records


def get_one_request(rowid):
    records = ''
    sqlite_connection = sqlite3.connect('users.db')
    cursor = sqlite_connection.cursor()
    try:
        sqlite_select_query = """SELECT * from m_chat_id where rowid = ?"""
        cursor.execute(sqlite_select_query, (rowid,))
        records = cursor.fetchone()
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
    return records


def change_status(rowid):
    sqlite_connection = sqlite3.connect('users.db')
    cursor = sqlite_connection.cursor()
    try:
        cursor.execute("""
          UPDATE m_chat_id SET status = ?
          WHERE rowid = ?;
      """, (3, rowid))
        sqlite_connection.commit()
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()


def add_to_db(message, fio, guest_fio, date, time):
    sqlite_connection = sqlite3.connect('users.db')
    cursor = sqlite_connection.cursor()
    try:
        cursor.execute("INSERT INTO m_chat_id VALUES(NULL,?,?,?,?,?,?);",
                       [message.chat.id, fio, guest_fio, date, time, 0])
        sqlite_connection.commit()
        cursor.close()
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
    return str(cursor.lastrowid)
