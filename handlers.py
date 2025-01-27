# telegram_bot/handlers.py

import requests
import json
from db import get_default_balance, decrement_balance, calculate_price_per_generation, get_on_markup_percentage, notify_admin

PROXY_API_KEY = 'YOUR_PROXY_API_KEY'

def handle_start(bot, message, notify_admin_func):
    user_id = message.from_user.id
    username = message.from_user.username

    cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.execute("INSERT INTO users (telegram_id, balance) VALUES (?, ?)", (user_id, get_default_balance()))
        conn.commit()
        bot.send_message(user_id, f"Привет, {username}! Ваш запрос отправлен на одобрение администратором.")
        notify_admin_func(f"Новый пользователь: @{username}, ID: {user_id}")
    else:
        bot.send_message(user_id, "Вы уже зарегистрированы!")

def handle_generate(bot, message):
    user_id = message.from_user.id
    cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (user_id,))
    user = cursor.fetchone()

    if not user or not user[3]:  # Проверка на одобрение и наличие баланса
        bot.send_message(user_id, "Ваш аккаунт не одобрен или у вас закончился баланс генераций.")
        return

    bot.send_message(user_id, "Введите ваш запрос для генерации изображения:")
    bot.register_next_step_handler(message, process_generation_request)

def process_generation_request(message):
    user_id = message.from_user.id
    request_text = message.text

    response = generate_image_with_dalle(request_text)
    if response:
        bot.send_photo(user_id, response)
        decrement_balance(user_id)
    else:
        bot.send_message(user_id, "Произошла ошибка при генерации изображения.")

def generate_image_with_dalle(prompt):
    url = "https://api.proxyapi.ru/openai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PROXY_API_KEY}"
    }
    data = {
        "model": "dall-e-2",
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        result = response.json()
        image_url = result['data'][0]['url']  # Предположим, что результат содержит URL изображения
        return image_url
    return None

def decrement_balance(user_id):
    cursor.execute("UPDATE users SET balance = balance - 1 WHERE telegram_id = ?", (user_id,))
    conn.commit()

def handle_balance(bot, message):
    user_id = message.from_user.id
    cursor.execute("SELECT balance FROM users WHERE telegram_id = ?", (user_id,))
    balance = cursor.fetchone()[0]
    bot.send_message(user_id, f"Ваш текущий баланс: {balance} генераций.")

def handle_buy(bot, message, get_on_markup_percentage_func, save_payment_func):
    user_id = message.from_user.id
    msg = bot.send_message(user_id, "Введите количество генераций, которые вы хотите купить:")
    bot.register_next_step_handler(msg, lambda m: process_buy_request(m, bot, get_on_markup_percentage_func, save_payment_func))

def process_buy_request(message, bot, get_on_markup_percentage_func, save_payment_func):
    user_id = message.from_user.id
    try:
        num_generations = int(message.text)
        price_per_generation = calculate_price_per_generation(get_on_markup_percentage_func())
        total_cost = num_generations * price_per_generation

        markup = types.InlineKeyboardMarkup()
        confirm_button = types.InlineKeyboardButton("Оплатить", callback_data=f'pay_{num_generations}_{total_cost}')
        cancel_button = types.InlineKeyboardButton("Отмена", callback_data='cancel')
        markup.add(confirm_button, cancel_button)

        bot.send_message(user_id, f"Итого: {total_cost} ₽. Подтвердите оплату:", reply_markup=markup)
    except ValueError:
        bot.send_message(user_id, "Пожалуйста, введите корректное число.")

def calculate_price_per_generation(on_markup_percentage):
    base_price = 5.76  # Примерная цена за одну генерацию
    return base_price * (1 + on_markup_percentage)

def handle_callback(bot, call, notify_admin_func, save_payment_func):
    if call.data.startswith('pay_'):
        parts = call.data.split('_')
        num_generations = int(parts[1])
        total_cost = float(parts[2])
        user_id = call.from_user.id

        payment_id = save_payment_func(user_id, total_cost)
        notify_admin_func(f"Пользователь {user_id} хочет купить {num_generations} генераций на сумму {total_cost} ₽. ID платежа: {payment_id}")

        bot.send_message(user_id, "Ожидайте подтверждения оплаты от администратора.")
    elif call.data == 'cancel':
        bot.send_message(call.from_user.id, "Операция отменена.")
