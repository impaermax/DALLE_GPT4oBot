# telegram_bot/admin_panel.py

import telebot
from telebot import types
from db import get_on_markup_percentage, update_settings, generate_report

YOUR_ADMIN_TELEGRAM_ID = 1200223081
def handle_admin_panel(bot, message, update_settings_func, generate_report_func):
    user_id = message.from_user.id
    if user_id == YOUR_ADMIN_TELEGRAM_ID:  # Замените на реальный ID администратора
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Настройки"), types.KeyboardButton("Отчет"))
        bot.send_message(user_id, "Админ панель:", reply_markup=markup)
    else:
        bot.send_message(user_id, "У вас нет доступа к этой команде.")

def handle_admin_commands(bot, message, update_settings_func, generate_report_func):
    user_id = message.from_user.id
    if user_id == YOUR_ADMIN_TELEGRAM_ID:
        if message.text == "Настройки":
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Изменить наценку", callback_data='change_markup'))
            bot.send_message(user_id, "Выберите действие:", reply_markup=markup)
        elif message.text == "Отчет":
            report = generate_report_func()
            bot.send_message(user_id, report)

def handle_admin_callback(bot, call, update_settings_func, generate_report_func):
    user_id = call.from_user.id
    if user_id == YOUR_ADMIN_TELEGRAM_ID:
        if call.data == 'change_markup':
            msg = bot.send_message(user_id, "Введите новое значение наценки в процентах:")
            bot.register_next_step_handler(msg, lambda m: update_markup_percentage(m, bot, update_settings_func))
        elif call.data == 'report':
            report = generate_report_func()
            bot.send_message(user_id, report)

def update_markup_percentage(message, bot, update_settings_func):
    try:
        new_percentage = float(message.text) / 100
        update_settings_func('on_markup_percentage', new_percentage)
        bot.send_message(message.from_user.id, f"Наценка успешно изменена на {message.text}%.")
    except Exception as e:
        bot.send_message(message.from_user.id, "Ошибка при изменении наценки.")
