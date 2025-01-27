# telegram_bot/utils.py

import telebot

def notify_admin(text, bot, admin_id):
    bot.send_message(admin_id, text)
