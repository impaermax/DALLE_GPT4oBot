# telegram_bot/bot.py

import telebot
from telebot import types
from db import init_db, get_on_markup_percentage, get_default_balance, save_payment, update_settings, generate_report
from handlers import handle_start, handle_generate, handle_balance, handle_buy, handle_callback, notify_admin
from admin_panel import handle_admin_panel

# Инициализация бота
API_TOKEN = '7937346503:AAGj7dW3lOMbfTv4XO0W-Jr_rPDB9b8sA_A'
bot = telebot.TeleBot(API_TOKEN)

# Подключение к базе данных
init_db()

@bot.message_handler(commands=['start'])
def start(message):
    handle_start(bot, message, notify_admin)

@bot.message_handler(commands=['generate'])
def generate(message):
    handle_generate(bot, message)

@bot.message_handler(commands=['balance'])
def balance(message):
    handle_balance(bot, message)

@bot.message_handler(commands=['buy'])
def buy(message):
    handle_buy(bot, message, get_on_markup_percentage, save_payment)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    handle_callback(bot, call, notify_admin, save_payment)

@bot.message_handler(commands=['admin'])
def admin(message):
    handle_admin_panel(bot, message, update_settings, generate_report)

if __name__ == '__main__':
    bot.polling(none_stop=True)
