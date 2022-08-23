import telebot
import var
import basicui
import dal
import dop

import i18n

i18n.load_path.append('.')
i18n.set('locale', 'ru')

bot = telebot.TeleBot(var.Token)


def start(message):
    bot.send_message(message.chat.id, 'Все заявки приходят сюда. Какие заявки тебя интересуют?',
                     reply_markup=basicui.create_buttons(
                         [i18n.t('text.get_actual_requests'), i18n.t('text.get_today_requests'),
                          i18n.t('text.get_all_requests')]))


def handle_text(message):
    records = 0
    if message.text == i18n.t('text.get_actual_requests'):
        records = dal.get_actual_requests()
    elif message.text == i18n.t('text.get_today_requests'):
        records = dal.get_today_requests()
    elif message.text == i18n.t('text.get_all_requests'):
        records = dal.get_all_requests()
    if records != 0:
        if len(records) == 0:
            bot.send_message(message.chat.id, i18n.t('text.no_requests'))
        for row in records:
            bot.send_message(message.chat.id,
                             i18n.t('text.one_request', rowid=row[0], fio=row[2], guest_fio=row[3], date=row[4],
                                    time=row[5], symbol=dop.get_status_symbol(row)), parse_mode="Markdown")
    if message.chat.id == var.security_chat_id and message.text != i18n.t(
            'text.get_actual_requests') and message.text != i18n.t(
            'text.get_today_requests') and message.text != i18n.t('text.get_all_requests'):
        if message.text == i18n.t('text.skip'):
            message_next = message.id - 1
            security_decision(message, message_next)
        else:
            try:
                int(message.text)
                rowid = message.text
                return security_request(rowid)
            except ValueError:
                print('error')


def security_request(rowid):
    record = dal.get_one_request(rowid)
    if record:
        dop.get_status_symbol(record)
        tmp = i18n.t('text.one_request', rowid=str(record[0]), fio=str(record[2]), guest_fio=str(record[3]),
                     date=str(record[4]), time=str(record[5]), symbol=dop.get_status_symbol(record))
        msg = bot.send_message(var.security_chat_id, tmp, reply_markup=basicui.create_buttons([i18n.t('text.skip')]),
                               parse_mode="Markdown")
        bot.register_next_step_handler(msg, security_decision, rowid)
        return rowid
    else:
        bot.send_message(var.security_chat_id, 'Нет такой заявки')
    return -1


def security_decision(message, rowid):
    rowid = str(rowid)
    if message.text == i18n.t('text.skip'):
        dal.change_status(rowid)
        bot.send_message(var.security_chat_id, 'Ок.',
                         reply_markup=basicui.create_buttons([i18n.t('text.get_today_requests')]))
