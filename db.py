# telegram_bot/db.py

import sqlite3

conn = sqlite3.connect('bot.db', check_same_thread=False)
cursor = conn.cursor()

def init_db():
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        telegram_id INTEGER UNIQUE,
        balance INTEGER DEFAULT 0,
        is_approved BOOLEAN DEFAULT FALSE
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL,
        status TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')

    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('on_markup_percentage', ?)", ('0.35',))
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('default_balance', ?)", ('3',))

    conn.commit()

def get_on_markup_percentage():
    cursor.execute("SELECT value FROM settings WHERE key = 'on_markup_percentage'")
    return float(cursor.fetchone()[0])

def get_default_balance():
    cursor.execute("SELECT value FROM settings WHERE key = 'default_balance'")
    return int(cursor.fetchone()[0])

def save_payment(user_id, amount):
    cursor.execute("INSERT INTO payments (user_id, amount, status) VALUES (?, ?, ?)", (user_id, amount, 'pending'))
    conn.commit()
    return cursor.lastrowid

def update_settings(key, value):
    cursor.execute("UPDATE settings SET value = ? WHERE key = ?", (str(value), key))
    conn.commit()

def generate_report():
    cursor.execute("SELECT COUNT(*) FROM payments WHERE status = 'completed'")
    paid_users_count = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(amount) FROM payments WHERE status = 'completed'")
    total_income = cursor.fetchone()[0] or 0

    return f"Количество оплаченных пользователей: {paid_users_count}\nОбщий доход: {total_income} ₽"
