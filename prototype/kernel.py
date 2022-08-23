import gateway
import telebot
import dal
import basicui
import datetime
import re
from telebot import types
import var
import dop
import admin
import i18n

i18n.load_path.append('.')
i18n.set('locale', 'ru')

bot = telebot.TeleBot(var.Token)


@bot.message_handler(commands=["start"])
def start(message):
    dal.create_db()
    if message.chat.id != var.adm_chat_id and message.chat.id != var.security_chat_id:
        bot.send_message(message.chat.id, i18n.t('text.hi'),
                         reply_markup=basicui.create_buttons([i18n.t('text.invite'), i18n.t('text.show_status')]))
    else:
        admin.start(message)


@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.chat.id != var.adm_chat_id and message.chat.id != var.security_chat_id:
        if message.text == i18n.t('text.invite') or message.text == i18n.t('text.change_request'):
            msg = bot.send_message(message.chat.id, 'Напиши свои ФИО',
                                   reply_markup=basicui.create_buttons([i18n.t('text.cancel')]))
            bot.register_next_step_handler(msg, guest_fio)
        elif message.text == i18n.t('text.show_status'):
            show_status(message)
        else:
            bot.send_message(message.chat.id, 'Пиши разборчиво',
                             reply_markup=basicui.create_buttons(
                                 [i18n.t('text.invite'), i18n.t('text.show_status')]))
    else:
        k = admin.handle_text(message)
        if k != -1:
            bot.register_next_step_handler(message, admin.security_decision, k)


def show_status(message):
    records = dal.get_status(message)
    if len(records) == 0:
        bot.send_message(message.chat.id, i18n.t('text.no_requests'))
    else:
        for row in records:
            bot.send_message(message.chat.id, i18n.t('text.one_request', rowid=row[0], fio=row[2], guest_fio=row[3],
                                                     date=row[4], time=row[5], symbol=dop.get_status_symbol(row)),
                             parse_mode="Markdown")


def guest_fio(message):
    if message.text == i18n.t('text.cancel'):
        remove(message, i18n.t('text.canceled'))
    else:
        msg = bot.send_message(message.chat.id, 'Напиши ФИО гостя')
        bot.register_next_step_handler(msg, visit_date, message.text)


def visit_date(message, fio):
    if message.text == i18n.t('text.cancel'):
        remove(message, i18n.t('text.canceled'))
    else:
        msg = bot.send_message(message.chat.id, 'Укажи дату визита', reply_markup=basicui.create_buttons(
            [i18n.t('text.tomorrow'), i18n.t('text.next_tomorrow'), 'Выбрать другой день']))
        bot.register_next_step_handler(msg, add_visit_data, fio, message.text)


def add_visit_data(message, fio, guest_fio):
    current_date = datetime.date.today()
    if message.text == i18n.t('text.cancel'):
        remove(message, i18n.t('text.canceled'))
    elif message.text == i18n.t('text.tomorrow'):
        date = current_date + datetime.timedelta(days=1)
        visit_time(message, date.strftime("%d.%m.%Y"), fio, guest_fio)
    elif message.text == i18n.t('text.next_tomorrow'):
        date = current_date + datetime.timedelta(days=2)
        visit_time(message, date.strftime("%d.%m.%Y"), fio, guest_fio)
    else:
        msg = bot.send_message(message.chat.id, 'Напиши дату визита в формте ДД.ММ.ГГГГ',
                               reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, other_date, fio, guest_fio)


def other_date(message, fio, guest_fio):
    if dop.delta_days(message.text) == 1:
        visit_time(message, message.text, fio, guest_fio)
    else:
        bot.send_message(message.chat.id, 'Ты меня за придурка-то не держи')
        add_visit_data(message, fio, guest_fio)


def visit_time(message, date, fio, guest_fio):
    if message.text == i18n.t('text.cancel'):
        remove(message, i18n.t('text.canceled'))
    else:
        msg = bot.send_message(message.chat.id, 'Напиши время(с 8:00 до 19:00)',
                               reply_markup=basicui.create_buttons([i18n.t('text.cancel')]))
        bot.register_next_step_handler(msg, add_visit_time, date, fio, guest_fio)


def add_visit_time(message, date, fio, guest_fio):
    time = message.text
    if re.fullmatch("\d{1,2}[:][0-5][0-9]", time):
        if (7 < int(time.split(':')[0])) and int(time.split(':')[0]) < 19:
            tmp = i18n.t('text.visit_time', fio=str(fio), guest_fio=str(guest_fio), date=str(date), time=str(time))
            msg = bot.send_message(message.chat.id, f"Проверь данные, все верно?\n\n{tmp}",
                                   reply_markup=basicui.create_buttons([i18n.t('text.all_good'),
                                                                        i18n.t('text.change_request')]),
                                   parse_mode="Markdown")
            bot.register_next_step_handler(msg, check_db, fio, guest_fio, date, time)
        else:
            bot.send_message(message.chat.id, 'В это время нельзя 😢')
            visit_time(message, date, fio, guest_fio)
    else:
        bot.send_message(message.chat.id, 'ПРОСТО НАПИШИ ВРЕМЯ, НЕ ВЫПЕНДРИВАЙСЯ!😡')
        visit_time(message, date, fio, guest_fio)


def check_db(message, fio, guest_fio, date, time):
    if message.text == i18n.t('text.change_request'):
        handle_text(message)
    elif message.text == i18n.t('text.all_good'):
        request_number = dal.add_to_db(message, fio, guest_fio, date, time)
        tmp = i18n.t('text.check_db', rowid=request_number, fio=str(fio), guest_fio=str(guest_fio), date=str(date),
                     time=str(time))
        send_notif_adm(tmp, request_number)
        remove(message, 'Заявка отправлена!')
    else:
        bot.send_message(message.chat.id,
                         'Тебе надо было просто нажать на одну из 2-х кнопок, теперь заполняй всё заново')
        handle_text(message)


def send_notif_adm(tmp, request_number):
    markup_inline = types.InlineKeyboardMarkup()
    btn_yes = types.InlineKeyboardButton(text="Подтвердить", callback_data='1,' + str(request_number))
    btn_no = types.InlineKeyboardButton(text="Отменить", callback_data='2,' + str(request_number))
    markup_inline.add(btn_yes, btn_no)
    bot.send_message(var.adm_chat_id, f"Пришла новая заявка!\n{tmp}", reply_markup=markup_inline, parse_mode="Markdown")


@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    gateway.state(call)


def remove(message, text):
    bot.send_message(message.chat.id, text,
                     reply_markup=basicui.create_buttons([i18n.t('text.invite'), i18n.t('text.show_status')]))


bot.polling(none_stop=True, interval=0)
