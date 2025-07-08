import sqlite3

conn = sqlite3.connect("uno.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    coins INTEGER DEFAULT 100
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS admins (
    username TEXT UNIQUE
)
""")

def add_user(uid, username):
    cursor.execute("INSERT OR IGNORE INTO users (id, username) VALUES (?, ?)", (uid, username))
    cursor.execute("UPDATE users SET username = ? WHERE id = ?", (username, uid))
    conn.commit()

def get_balance(uid):
    result = cursor.execute("SELECT coins FROM users WHERE id = ?", (uid,)).fetchone()
    return result[0] if result else 0

def update_balance(uid, amount):
    cursor.execute("UPDATE users SET coins = coins + ? WHERE id = ?", (amount, uid))
    conn.commit()

def set_balance(username, amount):
    cursor.execute("UPDATE users SET coins = ? WHERE username = ?", (amount, username))
    conn.commit()

def get_all_user_ids():
    return [row[0] for row in cursor.execute("SELECT id FROM users").fetchall()]

def transfer_coins(sender_username, receiver_username, amount):
    sender = cursor.execute("SELECT coins FROM users WHERE username = ?", (sender_username,)).fetchone()
    receiver = cursor.execute("SELECT id FROM users WHERE username = ?", (receiver_username,)).fetchone()
    if not sender or not receiver or sender[0] < amount:
        return False
    cursor.execute("UPDATE users SET coins = coins - ? WHERE username = ?", (amount, sender_username))
    cursor.execute("UPDATE users SET coins = coins + ? WHERE username = ?", (amount, receiver_username))
    conn.commit()
    return True

def get_leaderboard():
    return cursor.execute("SELECT username, coins FROM users ORDER BY coins DESC LIMIT 5").fetchall()

def purge_users():
    cursor.execute("DELETE FROM users")
    conn.commit()

def get_low_balance_users(threshold=10):
    return [row[0] for row in cursor.execute("SELECT username FROM users WHERE coins < ?", (threshold,)).fetchall()]

def add_admin(username):
    cursor.execute("INSERT OR IGNORE INTO admins (username) VALUES (?)", (username,))
    conn.commit()

def remove_admin(username):
    cursor.execute("DELETE FROM admins WHERE username = ?", (username,))
    conn.commit()

def get_admin_list():
    return [row[0] for row in cursor.execute("SELECT username FROM admins").fetchall()]
