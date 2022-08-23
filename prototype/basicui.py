from telebot import types


def create_buttons(buttons):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for but in buttons:
        but = types.KeyboardButton(but)
        markup.add(but)
    return markup
