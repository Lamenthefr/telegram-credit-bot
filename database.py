import sqlite3

conn = sqlite3.connect('bot.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    solde REAL DEFAULT 0
)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    payment_id TEXT,
    user_id INTEGER,
    montant REAL,
    status TEXT,
    currency TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)""")
conn.commit()

def create_user_if_not_exists(user_id, username):
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()

def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    return cursor.fetchone()

def update_solde(user_id, amount):
    cursor.execute("UPDATE users SET solde = solde + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()

def get_all_user_ids():
    cursor.execute("SELECT user_id FROM users")
    return [row[0] for row in cursor.fetchall()]

def count_users():
    cursor.execute("SELECT COUNT(*) FROM users")
    return cursor.fetchone()[0]

def count_documents():
    cursor.execute("SELECT COUNT(*) FROM payments WHERE status = 'paid'")
    return cursor.fetchone()[0]
