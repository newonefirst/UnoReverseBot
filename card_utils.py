import sqlite3
import time
import random
import json

DB_NAME = "deck.db"

# ---------- DB Connection ----------
def get_conn():
    return sqlite3.connect(DB_NAME)

# ---------- Table Setup ----------
def setup_tables():
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                uid INTEGER PRIMARY KEY,
                username TEXT,
                karma INTEGER DEFAULT 0,
                last_active INTEGER DEFAULT 0
            )
        """)
        c.execute("CREATE TABLE IF NOT EXISTS balance (uid INTEGER PRIMARY KEY, coins INTEGER)")
        c.execute("CREATE TABLE IF NOT EXISTS deck (file_id TEXT PRIMARY KEY, json TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS transfer_log (sender INTEGER, receiver INTEGER, amount INTEGER, timestamp INTEGER)")
        c.execute("CREATE TABLE IF NOT EXISTS earn_log (uid INTEGER PRIMARY KEY, last_earned INTEGER)")
        c.execute("CREATE TABLE IF NOT EXISTS duel_stats (uid INTEGER PRIMARY KEY, wins INTEGER, losses INTEGER, draws INTEGER)")
        conn.commit()

def setup_card_table():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_cards (
                uid INTEGER,
                file_id TEXT,
                name TEXT,
                power TEXT,
                value INTEGER,
                rarity TEXT,
                drawn_at INTEGER
            )
        """)



def create_streak_table():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS streaks (
                uid INTEGER PRIMARY KEY,
                streak_day INTEGER,
                last_claimed INTEGER
            )
        """)
        conn.commit()

def create_duel_table():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS duels (
                challenger INTEGER,
                opponent INTEGER,
                result TEXT,
                timestamp INTEGER
            )
        """)
        conn.commit()


def init_db():
    with get_conn() as conn:
        # 🧙 User Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                uid INTEGER PRIMARY KEY,
                username TEXT,
                coins INTEGER DEFAULT 0,
                karma INTEGER DEFAULT 0,
                equipped_spell TEXT
            )
        """)

        # 🎴 Card Deck Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS deck (
                file_id TEXT PRIMARY KEY,
                json TEXT
            )
        """)

        # 📦 User-Owned Cards
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_cards (
                uid INTEGER,
                file_id TEXT,
                name TEXT,
                power TEXT,
                value INTEGER,
                rarity TEXT,
                drawn_at INTEGER
            )
        """)

        # 🔁 Duel Records
        conn.execute("""
            CREATE TABLE IF NOT EXISTS duels (
                challenger TEXT,
                opponent TEXT,
                result TEXT,
                timestamp INTEGER
            )
        """)

        # 🔥 Streak Tracker
        conn.execute("""
            CREATE TABLE IF NOT EXISTS streaks (
                uid INTEGER PRIMARY KEY,
                streak_day INTEGER,
                last_claimed INTEGER
            )
        """)

        # 🙌 Blessings Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS blessings (
                uid INTEGER,
                blessing TEXT,
                received_at INTEGER
            )
        """)

        # ⚰️ Tomb Sacrifices
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tomb (
                uid INTEGER,
                name TEXT,
                rarity TEXT,
                sacrificed_at INTEGER
            )
        """)

        # 🗿 Relic Vault
        conn.execute("""
            CREATE TABLE IF NOT EXISTS relics (
                uid INTEGER,
                name TEXT,
                power TEXT,
                value INTEGER,
                rarity TEXT,
                forged_at INTEGER
            )
        """)

        # 🗝️ Artefact Vault
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_artefacts (
                uid INTEGER,
                name TEXT,
                effect TEXT,
                acquired_at INTEGER
            )
        """)

        conn.commit()


# ---------- Karma System ----------
def get_karma(uid):
    with get_conn() as conn:
        result = conn.execute("SELECT karma FROM users WHERE uid=?", (uid,)).fetchone()
        return result[0] if result else 0

def update_karma(uid, new_value):
    with get_conn() as conn:
        conn.execute("UPDATE users SET karma=? WHERE uid=?", (new_value, uid))
        conn.commit()

def format_karma(k):
    if k < 100:
        return f"⭐ {k}"
    elif k < 1_000:
        return f"🌟 {k}"
    elif k < 1_000_000:
        return f"🔥 {k // 1_000}K"
    else:
        return f"⚡ {k:.2e}"

def ensure_karma_column():
    with get_conn() as conn:
        try:
            conn.execute("ALTER TABLE users ADD COLUMN karma INTEGER DEFAULT 0")
            print("✅ karma column added.")
        except sqlite3.OperationalError:
            print("⚠️ karma column already exists or failed.")
        conn.commit()

# ---------- Balance Management ----------
def get_balance(uid):
    with get_conn() as conn:
        result = conn.execute("SELECT coins FROM balance WHERE uid=?", (uid,)).fetchone()
        return result[0] if result else 0

def update_balance(uid, amount, overwrite=False):
    with get_conn() as conn:
        current = amount if overwrite else get_balance(uid) + amount
        conn.execute("REPLACE INTO balance (uid, coins) VALUES (?, ?)", (uid, current))

# ---------- Card Vault ----------
def add_card(file_id, json_data):
    with get_conn() as conn:
        conn.execute("INSERT OR REPLACE INTO deck (file_id, json) VALUES (?, ?)", (file_id, json_data))
        return True

def get_card_by_index(index):
    with get_conn() as conn:
        rows = conn.execute("SELECT json FROM deck").fetchall()
        if 0 <= index < len(rows):
            try:
                return json.loads(rows[index][0])
            except:
                return None
        return None

def remove_card_by_index(index):
    with get_conn() as conn:
        rows = conn.execute("SELECT file_id, json FROM deck").fetchall()
        if 0 <= index < len(rows):
            file_id, raw_json = rows[index]
            try:
                card = json.loads(raw_json)
                name = card.get("name", "")
                conn.execute("DELETE FROM deck WHERE file_id=?", (file_id,))
                conn.commit()
                return name
            except:
                return None
        return None


def remove_card(file_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM deck WHERE file_id=?", (file_id,))

def remove_card_by_name(name):
    with get_conn() as conn:
        rows = conn.execute("SELECT file_id, json FROM deck").fetchall()
        for file_id, raw_json in rows:
            try:
                card = json.loads(raw_json)
                if card.get("name", "").lower() == name.lower():
                    conn.execute("DELETE FROM deck WHERE file_id=?", (file_id,))
                    conn.commit()
                    return True
            except Exception as e:
                continue
    return False


def get_deck_size():
    with get_conn() as conn:
        result = conn.execute("SELECT COUNT(*) FROM deck").fetchone()
        return result[0] if result else 0

def list_all_cards():
    with get_conn() as conn:
        rows = conn.execute("SELECT json FROM deck").fetchall()
        cards = []
        for row in rows:
            try:
                card = json.loads(row[0])
                cards.append(card)
            except:
                continue
        return cards

def get_random_card():
    cards = list_all_cards()
    if not cards:
        return {
            "name": "Void Pulse",
            "power": "none",
            "value": 0,
            "rarity": "common",
            "cost": 0,
            "file_id": None
        }
    return random.choice(cards)

def get_spell_shop(limit=20):
    with get_conn() as conn:
        rows = conn.execute("SELECT file_id, json FROM deck LIMIT ?", (limit,)).fetchall()
        shop = []
        for file_id, json_data in rows:
            try:
                card = json.loads(json_data)
                card["file_id"] = file_id
                shop.append(card)
            except:
                continue
        return shop

def get_spell_by_power(power_name):
    with get_conn() as conn:
        rows = conn.execute("SELECT file_id, json FROM deck").fetchall()
        for file_id, json_data in rows:
            try:
                card = json.loads(json_data)
                if card.get("power") == power_name:
                    card["file_id"] = file_id
                    return card
            except:
                continue
        return None

def get_user_relics(uid):
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT name, power, value, rarity
            FROM relics
            WHERE uid=?
        """, (uid,)).fetchall()

    relics = []
    for name, power, value, rarity in rows:
        relics.append({
            "name": name,
            "power": power,
            "value": value,
            "rarity": rarity
        })
    return relics


def get_user_artefacts(uid):
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT name, effect
            FROM user_artefacts
            WHERE uid=?
        """, (uid,)).fetchall()

    artefacts = []
    for name, effect in rows:
        artefacts.append({
            "name": name,
            "effect": effect
        })
    return artefacts


# ---------- Rarity Boost ----------
def apply_rarity_bonus(card):
    rarity = card.get("rarity", "common").lower()
    base_value = card.get("value", 0)
    boost_map = {
        "uncommon": 0.10,
        "rare": 0.25,
        "epic": 0.40,
        "legendary": 0.60,
        "mythic": 0.75,
        "divine": 0.90,
        "shadow": 1.20
    }
    bonus = int(base_value * boost_map.get(rarity, 0))
    card["value"] = base_value + bonus
    return card

# ---------- Earn System ----------
def can_earn(uid, cooldown=86400):  # 24 hours
    with get_conn() as conn:
        result = conn.execute("SELECT last_earned FROM earn_log WHERE uid=?", (uid,)).fetchone()
        now = int(time.time())
        if not result or now - result[0] >= cooldown:
            conn.execute("REPLACE INTO earn_log (uid, last_earned) VALUES (?, ?)", (uid, now))
            return True
        return False

def update_earn_time(uid, timestamp=None):
    with get_conn() as conn:
        if timestamp is None:
            timestamp = int(time.time())
        conn.execute("REPLACE INTO earn_log (uid, last_earned) VALUES (?, ?)", (uid, timestamp))

# ---------- Transfers ----------
def log_transfer(sender, receiver, amount):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO transfer_log (sender, receiver, amount, timestamp) VALUES (?, ?, ?, ?)",
            (sender, receiver, amount, int(time.time()))
        )

def get_transfer_logs(limit=10):
    with get_conn() as conn:
        return conn.execute(
            "SELECT sender, receiver, amount, timestamp FROM transfer_log ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        ).fetchall()

# ---------- User Handling ----------
def track_user(uid, username):
    timestamp = int(time.time())
    with get_conn() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO users (uid, username, karma, last_active)
            VALUES (?, ?, COALESCE((SELECT karma FROM users WHERE uid=?), 0), ?)
        """, (uid, username, uid, timestamp))

def get_recent_users(seconds=300):
    now = int(time.time())
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT username FROM users WHERE ? - last_active < ?",
            (now, seconds)
        ).fetchall()
        return [f"@{r[0]}" for r in rows if r[0]]

def get_username(uid):
    with get_conn() as conn:
        result = conn.execute("SELECT username FROM users WHERE uid=?", (uid,)).fetchone()
        return result[0] if result and result[0] else "None"

def ensure_last_active_column():
    with get_conn() as conn:
        try:
            conn.execute("ALTER TABLE users ADD COLUMN last_active INTEGER DEFAULT 0")
            print("✅ last_active column added.")
        except sqlite3.OperationalError:
            print("⚠️ last_active column already exists or failed.")
        conn.commit()


def track_group(chat_id, title):
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS known_groups (
                chat_id INTEGER PRIMARY KEY,
                title TEXT
            )
        """)
        conn.execute("""
            INSERT OR IGNORE INTO known_groups (chat_id, title)
            VALUES (?, ?)
        """, (chat_id, title))
        conn.commit()




# ---------- Leaderboard ----------
def get_duel_rank(identifier=None, limit=10):
    conn = get_conn()

    # If no identifier is provided, return top duelists
    if identifier is None:
        rows = conn.execute("""
            SELECT challenger, COUNT(*) AS wins
            FROM duels
            WHERE result = 'win'
            GROUP BY challenger
            ORDER BY wins DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return rows

    # If identifier is an integer, treat as UID
    if isinstance(identifier, int):
        rows = conn.execute("""
            SELECT COUNT(*) AS wins,
                   SUM(CASE WHEN result = 'loss' THEN 1 ELSE 0 END) AS losses,
                   SUM(CASE WHEN result = 'draw' THEN 1 ELSE 0 END) AS draws
            FROM duels
            WHERE challenger = ? OR opponent = ?
        """, (identifier, identifier)).fetchone()
        return rows

    # If identifier is a string, treat as username
    if isinstance(identifier, str):
        # First, resolve UID from username
        row = conn.execute("SELECT uid FROM users WHERE username = ?", (identifier,)).fetchone()
        if not row:
            return (0, 0, 0)  # No data found
        uid = row[0]
        return get_duel_rank(uid)

    return (0, 0, 0)  # Fallback


# ---------- Duel Stats ----------
def get_duel_stats(uid):
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS duel_stats (
                uid INTEGER PRIMARY KEY,
                wins INTEGER,
                losses INTEGER,
                draws INTEGER
            )
        """)
        row = conn.execute("SELECT wins, losses, draws FROM duel_stats WHERE uid=?", (uid,)).fetchone()
        if row:
            return {"wins": row[0], "losses": row[1], "draws": row[2]}
        else:
            return {"wins": 0, "losses": 0, "draws": 0}

def update_duel_stats(uid, own_power, enemy_power):
    stats = get_duel_stats(uid)
    if own_power > enemy_power:
        stats["wins"] += 1
    elif own_power < enemy_power:
        stats["losses"] += 1
    else:
        stats["draws"] += 1

    with get_conn() as conn:
        conn.execute(
            "REPLACE INTO duel_stats (uid, wins, losses, draws) VALUES (?, ?, ?, ?)",
            (uid, stats["wins"], stats["losses"], stats["draws"])
        )


def get_user_relics(uid):
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT name, power, value, rarity
            FROM relics
            WHERE uid=?
        """, (uid,)).fetchall()

    relics = []
    for name, power, value, rarity in rows:
        relics.append({
            "name": name,
            "power": power,
            "value": value,
            "rarity": rarity
        })
    return relics


