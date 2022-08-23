import sqlite3
import var
import telebot
import i18n

bot = telebot.TeleBot(var.Token)


def state(call):
    sqlite_connection = sqlite3.connect('users.db')
    cursor = sqlite_connection.cursor()
    tmp = ''
    try:
        sqlite_select_query = """SELECT * from m_chat_id where rowid = ?"""
        cursor.execute(sqlite_select_query, (call.data.split(",")[1],))
        record = cursor.fetchone()
        tmp = i18n.t('text.check_db', rowid=str(record[0]), fio=str(record[2]), guest_fio=str(record[3]),
                     date=str(record[4]), time=str(record[5]))

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        try:
            cursor.execute("""
              UPDATE m_chat_id SET status = ?
              WHERE rowid = ?;
          """, (call.data.split(",")[0], call.data.split(",")[1]))
            sqlite_connection.commit()

            if call.data.split(",")[0] == '1':
                bot.answer_callback_query(call.id, 'Заявка одобрена')
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=f"{tmp}\nСтатус: ОДОБРЕНО ✅")
            elif call.data.split(",")[0] == '2':
                bot.answer_callback_query(call.id, 'Заявка не одобрена')
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=f"{tmp}\nСтатус: ОТКАЗАНО ⛔️")

        except sqlite_connection.Error:
            if sqlite_connection:
                sqlite_connection.rollback()

        if sqlite_connection:
            sqlite_connection.close()
