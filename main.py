# === System & Core ===
import logging, json, random, time, sqlite3

# === Ephemeral caches ===
pending_heart       = {}
pending_proposal    = {}
last_itachi_reward  = {}   # ← add this line


# === Telegram Bot Framework ===
from telegram import (
    Update, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
)
from telegram.constants import ChatMemberStatus
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ChatMemberHandler, ContextTypes, filters
)


from bank_utils import (
    assign_investor_badge,
    update_achievements,
    ASSET_LORE, 
    setup_dynamic_prices,
    seed_asset_prices,
    setup_badge_table,
    setup_achievements_table,
    setup_quest_table,
    setup_group_goals_table,
    get_asset_market, 
    buy_asset, 
    get_user_assets,
    fluctuate_asset_prices
)


from bank_utils import setup_bank_tables
setup_bank_tables()
setup_bank_tables()
setup_dynamic_prices()
seed_asset_prices()
setup_badge_table()
setup_achievements_table()
setup_quest_table()
setup_group_goals_table()


# === Utilities ===
from database import (
    add_user, get_balance, update_balance, set_balance,
    get_all_user_ids, transfer_coins, get_leaderboard,
    purge_users, get_low_balance_users,
    add_admin, remove_admin, get_admin_list
)

from card_utils import get_user_relics, get_user_artefacts
from card_utils import track_group

from card_utils import create_duel_table
create_duel_table()

from card_utils import init_db
init_db()

from card_utils import get_card_by_index
from card_utils import remove_card_by_name
from card_utils import (
    setup_tables, ensure_last_active_column, ensure_karma_column,
    get_conn, get_username, track_user, log_transfer,
    get_random_card, apply_rarity_bonus,
    get_spell_shop, get_spell_by_power, add_card, remove_card,
    list_all_cards, get_deck_size, can_earn, update_earn_time,
    get_recent_users, get_duel_rank, get_karma, format_karma
)

from duel_utils import (
    run_duel, update_duel_stats
)

# === Config ===
with open("config.json", "r") as f:
    config = json.load(f)

BOT_TOKEN = config.get("BOT_TOKEN")
ADMIN_IDS = config.get("ADMIN_IDS", [])

# === Logging ===
logging.basicConfig(level=logging.INFO)

# === Initial Setup ===
setup_tables()
ensure_last_active_column()
ensure_karma_column()

# === Help command ===

# 🧭 Help Command (angle-brackets escaped for HTML)
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🧭 <b>Welcome Shinobi!</b>\nHere are your available commands, grouped by category:\n\n"

        "💰 <b>Economy</b>\n"
        "• /earn — Claim daily coins\n"
        "• /balance — Check your coin balance\n"
        "• /give @user &lt;amount&gt; — Gift coins\n"
        "• /send @user &lt;amount&gt; — Send coins\n"
        "• /transfer @user &lt;amount&gt; — Transfer coins\n"
        "• /top — View leaderboard\n"
        "• /request &lt;amount&gt; — Request coins\n"

        "\n🎴 <b>Cards & Spells</b>\n"
        "• /draw — Draw a spell card\n"
        "• /mycards — View your cards\n"
        "• /steal — Attempt to steal a card\n"
        "• /spellbook — View available spells\n"
        "• /castspell &lt;name&gt; — Cast a spell\n"
        "• /equipspell &lt;name&gt; — Equip a spell\n"
        "• /unequipspell — Unequip your spell\n"
        "• /cardlist — List all available cards\n"
        "• /vault — View your relics & artefacts\n"
        "• /cardvault — View card vault\n"
        "• /prestigevault — View prestige cards\n"

        "\n⚔️ <b>Combat</b>\n"
        "• /challenge — Challenge someone to a duel\n"
        "• /duelrank — View your duel stats\n"
        "• /duelbadge — View your duel badge\n"
        "• /bossfight — Fight a boss\n"
        "• /shinobiarena — Enter the arena\n"
        "• /shinobibattle — Random shinobi battle\n"

        "\n🌟 <b>Karma & Tasks</b>\n"
        "• /karma — View your karma\n"
        "• /karmaquiz — Test your karma\n"
        "• /karmahall — View karma leaderboard\n"
        "• /dailymission — Get your daily mission\n"
        "• /shinobitask — Get your shinobi task\n"
        "• /claimstreak — Claim streak reward\n"
        "• /achievements — View your achievements\n"

        "\n🏪 <b>Market & Assets</b>\n"
        "• /assetmarket — Browse investment assets\n"
        "• /buyasset &lt;name&gt; — Purchase asset\n"
        "• /myassets — View your assets\n"
        "• /collectincome — Collect passive income\n"
        "• /sellasset &lt;name&gt; — Sell an asset\n"
        "• /assetinfo &lt;name&gt; — Info about an asset\n"
        "• /investrank — View top investors\n"
        "• /assetcompare A &#124; B — Compare two assets\n"
        "• /assettrend &lt;name&gt; — View price trend\n"
        "• /assetlore &lt;name&gt; — View lore\n"
        "• /bankstats — View global asset stats\n"
        "• /assettitle — Your asset-based title\n"

        "\n📖 <b>Progress & Quests</b>\n"
        "• /profilecard — View your profile\n"
        "• /shinobirank — Prestige leaderboard\n"
        "• /shinobititle — Your shinobi title\n"
        "• /shinobibadge — View your badge\n"
        "• /shinobilegacy — Your legacy stats\n"
        "• /questbook — View your quests\n"
        "• /groupgoal — View group goal\n"
        "• /clangoal — View clan-wide goal\n"

        "\n💘 <b>Romance & Fun</b>\n"
        "• /sendheart @user &lt;msg&gt; — Send heart publicly\n"
        "• /propose @user &lt;msg&gt; — Propose romantically\n"
        "• /npcvisit — Visit a random NPC\n"
        "• /shinobiquiz — Answer a shinobi quiz\n"
        "• /party — Tag active members\n"
        "• /shinobichest — Open a shinobi chest\n"

        "\n🛠️ <b>Utilities</b>\n"
        "• /start — Begin your journey\n"
        "• /help — Show this command list\n"
        "• /debugvault — View card debug\n"
        "• /getfileid — Get file ID from photo\n"

        "\n🩷 <i>Say 'Itachi is the best' once every 5 mins to earn coins</i>\n"
        "\n🌸 May your journey be guided by honor and wisdom."
    )
    await update.message.reply_text(help_text, parse_mode="HTML")





# === Bank Management ===

async def assetmarket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    assets = get_asset_market()
    if not assets:
        return await update.message.reply_text("📭 No assets available in ITACHI’S SECURE BANK.")

    lines = ["🏦 <b>ITACHI’S SECURE BANK — Asset Market</b>:"]
    for name, type_, cost, yield_, risk in assets:
        lines.append(
            f"🔹 <b>{name}</b> ({type_})\n"
            f"💰 Cost: {cost} coins\n"
            f"📈 Yield: {yield_}/day\n"
            f"⚠️ Risk: {risk}\n"
        )

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


async def buyasset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name

    if not context.args:
        return await update.message.reply_text("🛒 Usage: /buyasset <asset_name>")

    asset_name = " ".join(context.args).strip()

    # 🔍 Check if asset exists
    assets = get_asset_market()
    asset = next((a for a in assets if a[0].lower() == asset_name.lower()), None)
    if not asset:
        return await update.message.reply_text(f"❌ Asset '{asset_name}' not found in ITACHI’S SECURE BANK.")

    name, type_, _, yield_, risk = asset

    # 📈 Get latest price from asset_prices
    with get_conn() as conn:
        row = conn.execute("""
            SELECT price FROM asset_prices WHERE name=? ORDER BY timestamp DESC LIMIT 1
        """, (name,)).fetchone()
    if not row:
        return await update.message.reply_text("❌ No price data available for this asset.")
    cost = row[0]

    coins = get_balance(uid)
    if coins < cost:
        return await update.message.reply_text(
            f"🚫 You need {cost} coins to buy <b>{name}</b>. You only have {coins}.",
            parse_mode="HTML"
        )

    update_balance(uid, -cost)
    buy_asset(uid, name, 1)
    assign_investor_badge(uid)
    update_achievements(uid)

    await update.message.reply_text(
        f"✅ <b>{username}</b> purchased <b>{name}</b> from ITACHI’S SECURE BANK!\n"
        f"💰 Cost: {cost} coins\n📈 Daily Yield: {yield_} coins\n⚠️ Risk Level: {risk}",
        parse_mode="HTML"
    )


async def myassets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name

    assets = get_user_assets(uid)
    if not assets:
        return await update.message.reply_text(f"📭 <b>{username}</b>, you don’t own any assets yet.", parse_mode="HTML")

    lines = [f"💼 <b>{username}'s Portfolio — ITACHI’S SECURE BANK</b>:"]
    total_yield = 0

    for name, type_, cost, yield_, risk, qty in assets:
        income = yield_ * qty
        total_yield += income
        lines.append(
            f"🔸 <b>{name}</b> ({type_})\n"
            f"📦 Quantity: {qty}\n"
            f"📈 Daily Yield: {income} coins\n"
            f"⚠️ Risk: {risk}\n"
        )

    lines.append(f"\n💰 <b>Total Passive Income:</b> {total_yield} coins/day")
    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


async def collectincome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name

    now = int(time.time())
    assets = get_user_assets(uid)
    if not assets:
        return await update.message.reply_text(f"📭 <b>{username}</b>, you don’t own any assets yet.", parse_mode="HTML")

    total_income = 0

    with get_conn() as conn:
        for name, type_, cost, yield_, risk, qty in assets:
            row = conn.execute(
                "SELECT last_collected FROM user_assets WHERE uid=? AND asset_name=?",
                (uid, name)
            ).fetchone()

            last_collected = row[0] if row else 0
            elapsed = now - last_collected

            if elapsed >= 86400:
                income = yield_ * qty
                total_income += income
                conn.execute(
                    "UPDATE user_assets SET last_collected=? WHERE uid=? AND asset_name=?",
                    (now, uid, name)
                )

    if total_income == 0:
        return await update.message.reply_text("🕒 You’ve already collected income in the last 24 hours.")

    update_balance(uid, total_income)
    assign_investor_badge(uid)
    update_achievements(uid)

    await update.message.reply_text(
        f"✅ <b>{username}</b>, you’ve collected <b>{total_income}</b> coins from your assets!\n"
        f"🏦 Thank you for banking with ITACHI’S SECURE BANK.",
        parse_mode="HTML"
    )


async def sellasset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name

    if not context.args:
        return await update.message.reply_text("🧾 Usage: /sellasset <asset_name>")

    asset_name = " ".join(context.args).strip()

    assets = get_user_assets(uid)
    owned = next((a for a in assets if a[0].lower() == asset_name.lower()), None)
    if not owned:
        return await update.message.reply_text(f"❌ You don’t own any '{asset_name}' to sell.")

    name, type_, _, yield_, risk, qty = owned

    # 📈 Get current market price
    with get_conn() as conn:
        row = conn.execute("""
            SELECT price FROM asset_prices WHERE name=? ORDER BY timestamp DESC LIMIT 1
        """, (name,)).fetchone()
    if not row:
        return await update.message.reply_text("❌ No price data available for this asset.")
    current_price = row[0]

    refund = current_price * qty

    with get_conn() as conn:
        conn.execute("DELETE FROM user_assets WHERE uid=? AND asset_name=?", (uid, name))

    update_balance(uid, refund)
    assign_investor_badge(uid)
    update_achievements(uid)

    await update.message.reply_text(
        f"✅ <b>{username}</b> sold <b>{qty}x {name}</b> for <b>{refund}</b> coins at market price.\n"
        f"🏦 Thank you for banking with ITACHI’S SECURE BANK.",
        parse_mode="HTML"
    )

async def mintasset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return await update.message.reply_text("⛔ Only admins can mint new assets.")

    if len(context.args) < 5:
        return await update.message.reply_text(
            "🧾 Usage: /mintasset <name> | <type> | <cost> | <yield> | <risk>\n"
            "Example: /mintasset Silver Coin | metal | 250 | 8 | low"
        )

    raw = " ".join(context.args)
    parts = [p.strip() for p in raw.split("|")]
    if len(parts) != 5:
        return await update.message.reply_text("🚫 Invalid format. Use: name | type | cost | yield | risk")

    name, type_, cost, yield_, risk = parts
    try:
        cost = int(cost)
        yield_ = int(yield_)
    except ValueError:
        return await update.message.reply_text("🚫 Cost and yield must be numbers.")

    with get_conn() as conn:
        exists = conn.execute("SELECT 1 FROM assets WHERE name=?", (name,)).fetchone()
        if exists:
            return await update.message.reply_text(f"⚠️ Asset '{name}' already exists.")
        conn.execute(
            "INSERT INTO assets (name, type, cost, yield, risk) VALUES (?, ?, ?, ?, ?)",
            (name, type_, cost, yield_, risk)
        )

    await update.message.reply_text(
        f"✅ Minted new asset: <b>{name}</b>\n💰 Cost: {cost} coins\n📈 Yield: {yield_}/day\n⚠️ Risk: {risk}",
        parse_mode="HTML"
    )


async def investrank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT ua.uid, SUM(a.cost * ua.quantity) AS total_value
            FROM user_assets ua
            JOIN assets a ON ua.asset_name = a.name
            GROUP BY ua.uid
            ORDER BY total_value DESC
            LIMIT 10
        """).fetchall()

    if not rows:
        return await update.message.reply_text("📭 No investors found in ITACHI’S SECURE BANK.")

    lines = ["🏦 <b>Top Investors — ITACHI’S SECURE BANK</b>:"]
    for i, (uid, value) in enumerate(rows, start=1):
        username = get_username(uid)
        lines.append(f"{i}. <b>{username}</b> — 💼 Portfolio Value: {value} coins")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


async def assetinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("🔍 Usage: /assetinfo <asset_name>")

    asset_name = " ".join(context.args).strip()
    assets = get_asset_market()
    asset = next((a for a in assets if a[0].lower() == asset_name.lower()), None)

    if not asset:
        return await update.message.reply_text(f"❌ Asset '{asset_name}' not found in ITACHI’S SECURE BANK.")

    name, type_, cost, yield_, risk = asset

    await update.message.reply_text(
        f"📊 <b>Asset Info — {name}</b>\n"
        f"🏷️ Type: {type_}\n"
        f"💰 Cost: {cost} coins\n"
        f"📈 Daily Yield: {yield_} coins\n"
        f"⚠️ Risk Level: {risk}\n"
        f"🏦 Available in ITACHI’S SECURE BANK",
        parse_mode="HTML"
    )



async def assettrend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("📊 Usage: /assettrend <asset_name>")

    asset_name = " ".join(context.args).strip()
    with get_conn() as conn:
        history = conn.execute("""
            SELECT timestamp, price FROM asset_prices WHERE name=?
            ORDER BY timestamp DESC LIMIT 5
        """, (asset_name,)).fetchall()

    if not history:
        return await update.message.reply_text(f"❌ No price data found for '{asset_name}'.")

    lines = [f"📉 <b>Price Trend — {asset_name.title()}</b>:"]
    for ts, price in reversed(history):
        dt = time.strftime('%Y-%m-%d %H:%M', time.localtime(ts))
        lines.append(f"🕒 {dt} — 💰 {price} coins")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")



async def auditvault(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return await update.message.reply_text("⛔ Only admins can audit the vault.")

    with get_conn() as conn:
        rows = conn.execute("""
            SELECT a.type, SUM(a.cost * ua.quantity) AS total_value
            FROM user_assets ua
            JOIN assets a ON ua.asset_name = a.name
            GROUP BY a.type
        """).fetchall()

    if not rows:
        return await update.message.reply_text("📭 No assets found in the vault.")

    lines = ["🏛️ <b>Community Vault — ITACHI’S SECURE BANK</b>:"]
    total = 0
    for type_, value in rows:
        total += value
        lines.append(f"🔹 <b>{type_.title()}</b>: {value} coins")

    lines.append(f"\n💰 <b>Total Vault Value:</b> {total} coins")
    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


async def assetshare(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("📊 Usage: /assetshare <asset_name>")

    asset_name = " ".join(context.args).strip()
    with get_conn() as conn:
        count = conn.execute("""
            SELECT COUNT(DISTINCT uid) FROM user_assets WHERE asset_name=?
        """, (asset_name,)).fetchone()[0]

    await update.message.reply_text(
        f"📈 <b>{count}</b> users currently own <b>{asset_name.title()}</b>.",
        parse_mode="HTML"
    )


async def bankstats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with get_conn() as conn:
        total_users = conn.execute("SELECT COUNT(DISTINCT uid) FROM user_assets").fetchone()[0]
        total_assets = conn.execute("SELECT COUNT(*) FROM user_assets").fetchone()[0]
        total_income = conn.execute("""
            SELECT SUM(a.yield * ua.quantity)
            FROM user_assets ua
            JOIN assets a ON ua.asset_name = a.name
        """).fetchone()[0]

    await update.message.reply_text(
        f"📊 <b>ITACHI’S SECURE BANK — Global Stats</b>\n"
        f"👥 Investors: {total_users}\n"
        f"📦 Total Assets Held: {total_assets}\n"
        f"💰 Daily Passive Income Potential: {total_income} coins",
        parse_mode="HTML"
    )


async def assetcompare(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        return await update.message.reply_text("📊 Usage: /assetcompare <Asset A> | <Asset B>")

    raw = " ".join(context.args)
    parts = [p.strip() for p in raw.split("|")]
    if len(parts) != 2:
        return await update.message.reply_text("🚫 Format: Asset A | Asset B")

    a_name, b_name = parts
    assets = get_asset_market()
    a = next((x for x in assets if x[0].lower() == a_name.lower()), None)
    b = next((x for x in assets if x[0].lower() == b_name.lower()), None)

    if not a or not b:
        return await update.message.reply_text("❌ One or both assets not found.")

    def format_asset(data):
        name, type_, cost, yield_, risk = data
        return f"<b>{name}</b>\n💰 Cost: {cost}\n📈 Yield: {yield_}/day\n⚠️ Risk: {risk}\n🏷️ Type: {type_}"

    await update.message.reply_text(
        f"📊 <b>Asset Comparison</b>\n\n{format_asset(a)}\n\n🆚\n\n{format_asset(b)}",
        parse_mode="HTML"
    )


async def assetlore(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("📜 Usage: /assetlore <asset_name>")

    asset_name = " ".join(context.args).strip()
    lore = ASSET_LORE.get(asset_name.title())

    if not lore:
        return await update.message.reply_text(f"❌ No lore found for '{asset_name}'.")

    await update.message.reply_text(
        f"📜 <b>{asset_name.title()} Lore</b>\n{lore}",
        parse_mode="HTML"
    )



async def flashsale(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return await update.message.reply_text("⛔ Only admins can trigger flash sales.")

    if len(context.args) < 2:
        return await update.message.reply_text("🛍️ Usage: /flashsale <asset_name> <discount_percent>")

    asset_name = context.args[0]
    try:
        percent = int(context.args[1])
    except ValueError:
        return await update.message.reply_text("🚫 Discount must be a number.")

    apply_flash_discount(asset_name.title(), percent)
    await update.message.reply_text(
        f"🔥 <b>FLASH SALE!</b>\n<b>{asset_name.title()}</b> is now {percent}% off!\n🏦 Available at ITACHI’S SECURE BANK.",
        parse_mode="HTML"
    )

async def runbankengine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return await update.message.reply_text("⛔ Admin only.")

    auto_collect_income()
    scheduled_asset_appreciation()
    await update.message.reply_text("✅ Bank engine executed: income collected & asset prices updated.")


async def achievements(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name

    with get_conn() as conn:
        row = conn.execute("SELECT * FROM achievements WHERE uid=?", (uid,)).fetchone()

    if not row:
        return await update.message.reply_text(f"📭 <b>{username}</b>, no achievements found yet.", parse_mode="HTML")

    _, first, total, income, diversified = row
    join_date = time.strftime('%Y-%m-%d', time.localtime(first))

    await update.message.reply_text(
        f"🏅 <b>{username}'s Achievements — ITACHI’S SECURE BANK</b>\n"
        f"📆 First Investment: {join_date}\n"
        f"📦 Assets Owned: {total}\n"
        f"💰 Passive Income Potential: {income}/day\n"
        f"🌐 Diversification Score: {diversified} types",
        parse_mode="HTML"
    )


async def assettitle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    with get_conn() as conn:
        row = conn.execute("SELECT max_income, diversified FROM achievements WHERE uid=?", (uid,)).fetchone()

    if not row:
        return await update.message.reply_text("📭 No title yet. Start investing!")

    income, diversified = row
    if income >= 500 and diversified >= 4:
        title = "🌐 Shinobi Syndicate Leader"
    elif income >= 250:
        title = "📈 Strategic Tycoon"
    elif diversified >= 3:
        title = "🌀 Multi-Asset Ninja"
    else:
        title = "💼 Rising Investor"

    await update.message.reply_text(
        f"🏷️ <b>Your Title:</b> {title}\nKeep growing to unlock elite status!",
        parse_mode="HTML"
    )


async def questbook(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name

    lines = [f"📖 <b>{username}'s Questbook — ITACHI’S SECURE BANK</b>:"]

    with get_conn() as conn:
        for name, _ in QUESTS:
            row = conn.execute("SELECT completed FROM quests WHERE uid=? AND quest_name=?", (uid, name)).fetchone()
            status = "✅ Completed" if row and row[0] else "❌ Incomplete"
            lines.append(f"🔹 {name}: {status}")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


async def groupgoal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with get_conn() as conn:
        rows = conn.execute("SELECT goal_name, target, progress, completed FROM group_goals").fetchall()

    if not rows:
        return await update.message.reply_text("📭 No group goals found.")

    lines = ["🏯 <b>Clan Goals — ITACHI’S SECURE BANK</b>:"]
    for name, target, progress, done in rows:
        status = "✅ Completed" if done else f"🔄 {progress}/{target}"
        lines.append(f"🔹 {name}: {status}")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


async def fluctuateprices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return await update.message.reply_text("⛔ Admin only.")
    fluctuate_asset_prices()
    await update.message.reply_text("✅ Asset prices have been updated.")


# === New Updates ===

DAILY_TASKS = [
    "Draw 2 cards", "Give 50 coins", "Win a duel",
    "Cast a spell", "Check your karma", "Send coins",
    "Equip a spell", "Steal coins", "Upload a card", "Check your balance"
]

user_missions = {}

async def dailymission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid in user_missions:
        return await update.message.reply_text(f"📜 Your mission today:\n<b>{user_missions[uid]}</b>", parse_mode="HTML")

    task = random.choice(DAILY_TASKS)
    user_missions[uid] = task
    await update.message.reply_text(f"🎯 <b>Daily Mission</b>:\n{task}", parse_mode="HTML")

def get_streak(uid):
    with get_conn() as conn:
        row = conn.execute("SELECT streak_day, last_claimed FROM streaks WHERE uid=?", (uid,)).fetchone()
        return row if row else (0, 0)

def update_streak(uid, day, now):
    with get_conn() as conn:
        conn.execute("REPLACE INTO streaks (uid, streak_day, last_claimed) VALUES (?, ?, ?)", (uid, day, now))
        conn.commit()

async def claimstreak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    now = int(time.time())
    day, last = get_streak(uid)

    if now - last < 86400:
        return await update.message.reply_text("🕒 You've already claimed your streak today.")

    day = day + 1 if now - last < 172800 else 1
    reward = 50 + (day * 10)
    update_balance(uid, reward)
    update_streak(uid, day, now)

    await update.message.reply_text(
        f"🔥 <b>Streak Day {day}</b>\nYou earned <b>{reward}</b> coins!",
        parse_mode="HTML"
    )

async def profilecard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name

    coins = get_balance(uid)
    karma = get_karma(uid)
    wins, losses, draws = get_duel_rank(uid)  # ✅ Patched to use UID safely
    day, _ = get_streak(uid)

    # 🏷️ Title Logic
    if wins >= 50 and karma >= 100:
        title = "🌌 Shinobi Legend"
    elif wins >= 25:
        title = "⚔️ Duel Master"
    elif karma >= 50:
        title = "✨ Karma Sage"
    else:
        title = "🎴 Rising Shinobi"

    # 🧠 Prestige Score
    relics = get_user_relics(uid)
    artefacts = get_user_artefacts(uid)
    prestige = karma + len(relics)*100 + len(artefacts)*150

    await update.message.reply_text(
        f"🧙 <b>{username}'s Profile Card</b>\n"
        f"🏷️ Title: {title}\n"
        f"💰 Coins: {coins}\n"
        f"🌟 Karma: {format_karma(karma)}\n"
        f"🏆 Wins: {wins} | ❌ Losses: {losses} | 🤝 Draws: {draws}\n"
        f"🔥 Streak: {day} days\n"
        f"🧠 Prestige Score: {prestige}",
        parse_mode="HTML"
    )


async def bossfight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name

    boss = {
        "name": "Shadow Kurama",
        "hp": 150,
        "attack": random.randint(20, 40),
        "reward": random.randint(200, 500)
    }

    player_hp = 100
    boss_hp = boss["hp"]
    log = [f"⚔️ <b>{username} vs {boss['name']}</b>"]

    while player_hp > 0 and boss_hp > 0:
        player_hit = random.randint(15, 35)
        boss_hit = boss["attack"]

        boss_hp -= player_hit
        player_hp -= boss_hit

        log.append(f"🗡️ You hit for {player_hit} | 🧟 Boss hits for {boss_hit}")
        time.sleep(0.5)

    if player_hp > 0:
        update_balance(uid, boss["reward"])
        log.append(f"\n🏆 Victory! You earned {boss['reward']} coins.")
    else:
        log.append("\n💀 Defeated! Better luck next time.")

    await update.message.reply_text("\n".join(log), parse_mode="HTML")

async def clangoal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    goals = [
        {"name": "Donate 10,000 coins", "target": 10000, "progress": 0},
        {"name": "Win 50 duels", "target": 50, "progress": 0}
    ]

    lines = ["🏯 <b>Clan Goals</b>:"]
    for goal in goals:
        status = "✅ Completed" if goal["progress"] >= goal["target"] else f"🔄 {goal['progress']}/{goal['target']}"
        lines.append(f"🔹 {goal['name']}: {status}")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")

async def invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    link = f"https://t.me/YourBotUsername?start={uid}"
    await update.message.reply_text(
        f"🎁 <b>Invite Friends</b>\nShare this link:\n{link}\n\nEarn coins when they join!",
        parse_mode="HTML"
    )


async def duelnews(update: Update, context: ContextTypes.DEFAULT_TYPE):
    top_duelists = get_duel_rank(limit=5)
    if not top_duelists:
        return await update.message.reply_text("📭 No duel activity found.")

    lines = ["📰 <b>Duel Arena News</b>:"]
    for i, (uid, coins) in enumerate(top_duelists, start=1):
        username = get_username(uid)
        lines.append(f"{i}. <b>{username}</b> — {coins} coins")

    lines.append("\n⚔️ Duel heat rising! Who will claim the top spot?")
    await update.message.reply_text("\n".join(lines), parse_mode="HTML")

async def banknews(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT name, price FROM asset_prices
            WHERE timestamp >= strftime('%s','now','-1 day')
            ORDER BY price DESC LIMIT 5
        """).fetchall()

    if not rows:
        return await update.message.reply_text("📭 No recent asset activity.")

    lines = ["🏦 <b>Bank Market News</b>:"]
    for name, price in rows:
        lines.append(f"💹 <b>{name}</b> surged to <b>{price}</b> coins!")

    lines.append("\n🔥 Flash sales may be coming soon. Stay alert!")
    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


async def npcvisit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    npcs = [
        {"name": "Master Itachi", "quote": "True power comes from restraint."},
        {"name": "Rogue Trader", "quote": "I’ve got rare cards... for a price."},
        {"name": "Shadow Duelist", "quote": "Care to test your fate in the dark?"}
    ]
    npc = random.choice(npcs)
    await update.message.reply_text(
        f"👤 <b>{npc['name']} appears!</b>\n🗨️ \"{npc['quote']}\"",
        parse_mode="HTML"
    )


async def cardstats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cards = list_all_cards()
    if not cards:
        return await update.message.reply_text("📭 No cards found in the vault.")

    total = len(cards)
    rarity_count = {}
    for card in cards:
        rarity = card.get("rarity", "Unknown").title()
        rarity_count[rarity] = rarity_count.get(rarity, 0) + 1

    lines = [f"📊 <b>Card Vault Stats</b>\nTotal Cards: {total}"]
    for rarity, count in rarity_count.items():
        lines.append(f"🎴 {rarity}: {count}")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")

async def prestigevault(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cards = list_all_cards()
    if not cards:
        return await update.message.reply_text("📭 No cards found.")

    filtered = [c for c in cards if c.get("rarity", "").lower() in ["legendary", "mythic", "special mythic"]]
    if not filtered:
        return await update.message.reply_text("🔒 No prestige cards found.")

    lines = ["🏆 <b>Prestige Vault</b>:"]
    for card in filtered:
        lines.append(f"• <b>{card['name']}</b> | 🔮 {card['power']} | 💥 {card['value']} | 🎴 {card['rarity'].title()}")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")

QUIZ_QUESTIONS = [
    {"q": "Who is the founder of the bot’s bank system?", "a": "Itachi"},
    {"q": "What command lets you draw a spell card?", "a": "/draw"},
    {"q": "Which rarity is higher: Epic or Mythic?", "a": "Mythic"},
    {"q": "What does karma represent?", "a": "Reputation or honor"},
    {"q": "Which command shows your duel rank?", "a": "/duelrank"}
]

async def shinobiquiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = random.choice(QUIZ_QUESTIONS)
    await update.message.reply_text(
        f"🧠 <b>Shinobi Quiz</b>\n{q['q']}\n\nReply with your answer!",
        parse_mode="HTML"
    )

async def karmahall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT uid, karma FROM users
            ORDER BY karma DESC LIMIT 10
        """).fetchall()

    if not rows:
        return await update.message.reply_text("📭 No karma data found.")

    lines = ["🌟 <b>Karma Hall of Fame</b>:"]
    for i, (uid, karma) in enumerate(rows, start=1):
        username = get_username(uid)
        lines.append(f"{i}. <b>{username}</b> — ✨ {format_karma(karma)}")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")

async def duelbadge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    username = get_username(uid)
    wins, _, _ = get_duel_rank(username)

    if wins >= 100:
        badge = "👑 Grandmaster Duelist"
    elif wins >= 50:
        badge = "⚔️ Elite Shinobi"
    elif wins >= 25:
        badge = "🥷 Rising Challenger"
    else:
        badge = "🎴 Novice Duelist"

    await update.message.reply_text(
        f"🏅 <b>{username}'s Duel Badge</b>\nTitle: {badge}\nWins: {wins}",
        parse_mode="HTML"
    )

SHOP_ITEMS = [
    {"name": "Mythic Card Pack", "cost": 1000},
    {"name": "Karma Halo", "cost": 750},
    {"name": "Duel Boost", "cost": 500}
]

async def shinobishop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lines = ["🛍️ <b>Shinobi Prestige Shop</b>:"]
    for item in SHOP_ITEMS:
        lines.append(f"• <b>{item['name']}</b> — 💰 {item['cost']} coins")

    lines.append("\nUse /buyitem <item_name> to purchase.")
    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


async def buyitem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not context.args:
        return await update.message.reply_text("🛒 Usage: /buyitem <item_name>")

    item_name = " ".join(context.args).strip().lower()
    item = next((i for i in SHOP_ITEMS if i["name"].lower() == item_name), None)

    if not item:
        return await update.message.reply_text(f"❌ Item '{item_name}' not found in Shinobi Shop.")

    coins = get_balance(uid)
    if coins < item["cost"]:
        return await update.message.reply_text(f"🚫 You need {item['cost']} coins to buy '{item['name']}'. You have {coins}.")

    update_balance(uid, -item["cost"])
    await update.message.reply_text(
        f"✅ Purchased <b>{item['name']}</b> for <b>{item['cost']}</b> coins!\n🎁 Use it wisely, shinobi.",
        parse_mode="HTML"
    )


async def shinobititle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    username = get_username(uid)
    karma = get_karma(uid)
    wins, _, _ = get_duel_rank(username)

    if karma >= 100 and wins >= 50:
        title = "🌌 Shinobi Legend"
    elif karma >= 50:
        title = "✨ Karma Sage"
    elif wins >= 25:
        title = "⚔️ Duel Master"
    else:
        title = "🎴 Novice Shinobi"

    await update.message.reply_text(
        f"🏷️ <b>{username}'s Shinobi Title</b>\nTitle: {title}\n🌟 Karma: {format_karma(karma)}\n🏆 Wins: {wins}",
        parse_mode="HTML"
    )

KARMA_QUIZ = [
    {"q": "What triggers karma gain in this bot?", "a": "Reply with +1 or 👍"},
    {"q": "What command shows your karma?", "a": "/karma"},
    {"q": "What is karma used for?", "a": "Prestige, reputation, and titles"},
    {"q": "Can you give karma to yourself?", "a": "No"},
    {"q": "What boosts karma besides +1?", "a": "Saying 'itachi is best'"}
]

async def karmaquiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = random.choice(KARMA_QUIZ)
    await update.message.reply_text(
        f"🧠 <b>Karma Quiz</b>\n{q['q']}\n\nReply with your answer!",
        parse_mode="HTML"
    )


async def shinobirank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT uid, karma + (
                SELECT COUNT(*) FROM user_cards WHERE user_cards.uid = users.uid
            ) AS prestige_score
            FROM users
            ORDER BY prestige_score DESC
            LIMIT 10
        """).fetchall()

    if not rows:
        return await update.message.reply_text("📭 No prestige data found.")

    lines = ["🧭 <b>Shinobi Prestige Rank</b>:"]
    for i, (uid, score) in enumerate(rows, start=1):
        username = get_username(uid)
        lines.append(f"{i}. <b>{username}</b> — 🧠 Prestige: {score}")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")

async def shinobibadge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    coins = get_balance(uid)
    karma = get_karma(uid)
    cards = get_deck_size(uid)

    badges = []
    if coins >= 10000:
        badges.append("💰 Wealthy Shinobi")
    if karma >= 100:
        badges.append("✨ Karma Master")
    if cards >= 20:
        badges.append("🎴 Card Collector")

    if not badges:
        badges.append("🎴 Novice Shinobi")

    await update.message.reply_text(
        f"🏅 <b>Your Shinobi Badges</b>\n" + "\n".join(badges),
        parse_mode="HTML"
    )

async def shinobichest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    reward_type = random.choice(["coins", "karma", "card"])
    reward_msg = ""

    if reward_type == "coins":
        amount = random.randint(100, 500)
        update_balance(uid, amount)
        reward_msg = f"💰 You found <b>{amount}</b> coins!"
    elif reward_type == "karma":
        with get_conn() as conn:
            conn.execute("UPDATE users SET karma = karma + 5 WHERE uid=?", (uid,))
            conn.commit()
        reward_msg = "✨ You gained <b>5 karma</b>!"
    else:
        card = apply_rarity_bonus(get_random_card())
        with get_conn() as conn:
            conn.execute("""
                INSERT INTO user_cards (uid, file_id, name, power, value, rarity, drawn_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                uid,
                card.get("file_id"),
                card.get("name"),
                card.get("power"),
                card.get("value"),
                card.get("rarity"),
                int(time.time())
            ))
        reward_msg = f"🎴 You received a <b>{card['rarity'].title()}</b> card: <b>{card['name']}</b>!"

    await update.message.reply_text(f"🎁 <b>Shinobi Chest Opened!</b>\n{reward_msg}", parse_mode="HTML")

async def shinobiarena(update: Update, context: ContextTypes.DEFAULT_TYPE):
    top_duelists = get_duel_rank(limit=10)
    if not top_duelists:
        return await update.message.reply_text("📭 No duel data found.")

    lines = ["⚔️ <b>Shinobi Arena</b> — Top Duelists:"]
    for i, (uid, wins) in enumerate(top_duelists, start=1):
        username = get_username(uid)
        lines.append(f"{i}. <b>{username}</b> — 🏆 {wins} wins")

    lines.append("\n🔥 Arena is open. Challenge someone with /duel <username>")
    await update.message.reply_text("\n".join(lines), parse_mode="HTML")

SHINOBI_TASKS = [
    "Give karma to 3 users",
    "Win 2 duels today",
    "Send 100 coins to someone",
    "Equip a rare spell",
    "Draw 3 cards",
    "Check your prestige rank"
]

user_tasks = {}

async def shinobitask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid in user_tasks:
        return await update.message.reply_text(f"📜 Your current task:\n<b>{user_tasks[uid]}</b>", parse_mode="HTML")

    task = random.choice(SHINOBI_TASKS)
    user_tasks[uid] = task
    await update.message.reply_text(f"📜 <b>Shinobi Task</b>:\n{task}", parse_mode="HTML")

async def shinobiblessing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    blessings = [
        {"type": "karma", "amount": 5, "msg": "✨ You feel enlightened. +5 karma."},
        {"type": "coins", "amount": 250, "msg": "💰 A hidden monk gifts you 250 coins."},
        {"type": "title", "msg": "🌌 You are now known as 'Blessed Shinobi'."}
    ]
    blessing = random.choice(blessings)

    if blessing["type"] == "karma":
        with get_conn() as conn:
            conn.execute("UPDATE users SET karma = karma + ? WHERE uid=?", (blessing["amount"], uid))
            conn.commit()
    elif blessing["type"] == "coins":
        update_balance(uid, blessing["amount"])
    elif blessing["type"] == "title":
        # Optional: store title in user profile table
        pass

    await update.message.reply_text(f"🙏 <b>Shinobi Blessing</b>\n{blessing['msg']}", parse_mode="HTML")

async def shinobiforge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    inventory = get_user_inventory(uid)

    if len(inventory) < 2:
        return await update.message.reply_text("🛠️ You need at least 2 cards or spells to forge.")

    combo = random.sample(inventory, 2)
    new_card = {
        "name": f"{combo[0]['name']} + {combo[1]['name']}",
        "power": f"{combo[0]['power']} & {combo[1]['power']}",
        "value": combo[0]['value'] + combo[1]['value'] + random.randint(50, 150),
        "rarity": "Forged"
    }

    save_card_to_user(uid, new_card)
    await update.message.reply_text(
        f"🔨 <b>Forging Complete!</b>\nYou created a new card:\n<b>{new_card['name']}</b>\n🎴 Rarity: {new_card['rarity']}",
        parse_mode="HTML"
    )

async def shinobitrade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        return await update.message.reply_text("🔁 Usage: /shinobitrade <@username> <amount>")

    target_username = context.args[0].lstrip("@")
    amount = int(context.args[1])
    sender_id = update.effective_user.id
    receiver_id = get_uid_by_username(target_username)

    if not receiver_id:
        return await update.message.reply_text("❌ User not found.")

    if get_balance(sender_id) < amount:
        return await update.message.reply_text("🚫 You don't have enough coins.")

    update_balance(sender_id, -amount)
    update_balance(receiver_id, amount)

    await update.message.reply_text(
        f"✅ You sent <b>{amount}</b> coins to <b>@{target_username}</b>.",
        parse_mode="HTML"
    )

async def shinobialtar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    inventory = get_user_inventory(uid)

    if not inventory:
        return await update.message.reply_text("🕯️ You have no cards to sacrifice.")

    card = random.choice(inventory)
    remove_card_from_user(uid, card["name"])
    karma_gain = random.randint(3, 10)

    with get_conn() as conn:
        conn.execute("UPDATE users SET karma = karma + ? WHERE uid=?", (karma_gain, uid))
        conn.commit()

    await update.message.reply_text(
        f"🕯️ <b>Altar Ritual</b>\nYou sacrificed <b>{card['name']}</b>.\n✨ Gained <b>{karma_gain}</b> karma.",
        parse_mode="HTML"
    )

MARKET_ITEMS = [
    {"name": "Epic Card Pack", "cost": 800},
    {"name": "Spell Scroll", "cost": 500},
    {"name": "Karma Boost", "cost": 300}
]

async def shinobimarket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lines = ["🏪 <b>Shinobi Market</b>:"]
    for item in MARKET_ITEMS:
        lines.append(f"• <b>{item['name']}</b> — 💰 {item['cost']} coins")

    lines.append("\nUse /marketbuy <item_name> to purchase.")
    await update.message.reply_text("\n".join(lines), parse_mode="HTML")

async def shinobispell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    spell = get_equipped_spell(uid)

    if not spell:
        return await update.message.reply_text("🧙 You have no spell equipped. Use /equipspell to choose one.")

    await update.message.reply_text(
        f"🧙 <b>Equipped Spell</b>\nName: <b>{spell['name']}</b>\nEffect: {spell['effect']}",
        parse_mode="HTML"
    )

async def shinobitomb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    with get_conn() as conn:
        rows = conn.execute("SELECT name, rarity FROM tomb WHERE uid=?", (uid,)).fetchall()

    if not rows:
        return await update.message.reply_text("⚰️ No fallen cards or sacrifices found.")

    lines = ["⚰️ <b>Shinobi Tomb</b> — Your Sacrifices:"]
    for name, rarity in rows:
        lines.append(f"• <b>{name}</b> — 🎴 {rarity}")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")

async def equipspell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not context.args:
        return await update.message.reply_text("🧙 Usage: /equipspell <spell_name>")

    spell_name = " ".join(context.args).strip()
    spell = get_spell_by_name(uid, spell_name)

    if not spell:
        return await update.message.reply_text(f"❌ Spell '{spell_name}' not found in your inventory.")

    with get_conn() as conn:
        conn.execute("UPDATE users SET equipped_spell=? WHERE uid=?", (spell_name, uid))
        conn.commit()

    await update.message.reply_text(f"✅ Equipped spell: <b>{spell_name}</b>", parse_mode="HTML")


async def marketbuy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not context.args:
        return await update.message.reply_text("🛒 Usage: /marketbuy <item_name>")

    item_name = " ".join(context.args).strip().lower()
    item = next((i for i in MARKET_ITEMS if i["name"].lower() == item_name), None)

    if not item:
        return await update.message.reply_text(f"❌ Item '{item_name}' not found in Shinobi Market.")

    coins = get_balance(uid)
    if coins < item["cost"]:
        return await update.message.reply_text(f"🚫 You need {item['cost']} coins. You have {coins}.")

    update_balance(uid, -item["cost"])
    await update.message.reply_text(
        f"✅ Purchased <b>{item['name']}</b> for <b>{item['cost']}</b> coins!",
        parse_mode="HTML"
    )

async def tombstats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with get_conn() as conn:
        rows = conn.execute("SELECT rarity, COUNT(*) FROM tomb GROUP BY rarity").fetchall()
        total = sum(count for _, count in rows)

    if not rows:
        return await update.message.reply_text("⚰️ No sacrifices recorded yet.")

    lines = [f"⚰️ <b>Global Tomb Stats</b>\nTotal Sacrifices: {total}"]
    for rarity, count in rows:
        lines.append(f"• 🎴 {rarity.title()}: {count}")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")

async def shinobifusion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    inventory = get_user_inventory(uid)

    if len(inventory) < 2:
        return await update.message.reply_text("🧬 You need at least 2 cards to fuse.")

    combo = random.sample(inventory, 2)
    relic = {
        "name": f"{combo[0]['name']} × {combo[1]['name']}",
        "power": f"{combo[0]['power']} + {combo[1]['power']}",
        "value": combo[0]['value'] + combo[1]['value'] + random.randint(100, 300),
        "rarity": "Relic"
    }

    save_card_to_user(uid, relic)
    await update.message.reply_text(
        f"🧬 <b>Fusion Complete!</b>\nCreated Relic: <b>{relic['name']}</b>\n🎴 Rarity: {relic['rarity']}",
        parse_mode="HTML"
    )

async def shinobibattle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    opponent = random.choice(["Shadow Itachi", "Rogue Trader", "Mystic Monk"])
    player_hp = 100
    enemy_hp = 120
    log = [f"⚔️ <b>You vs {opponent}</b>"]

    while player_hp > 0 and enemy_hp > 0:
        hit = random.randint(20, 35)
        enemy_hit = random.randint(15, 30)
        enemy_hp -= hit
        player_hp -= enemy_hit
        log.append(f"🗡️ You hit {hit} | 👊 {opponent} hits {enemy_hit}")
        time.sleep(0.3)

    if player_hp > 0:
        reward = random.randint(300, 600)
        update_balance(uid, reward)
        log.append(f"\n🏆 Victory! You earned {reward} coins.")
    else:
        log.append("\n💀 Defeated! Train harder, shinobi.")

    await update.message.reply_text("\n".join(log), parse_mode="HTML")


async def shinobirelic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    relics = get_user_relics(uid)

    if not relics:
        return await update.message.reply_text("🗿 No relics found in your vault.")

    lines = ["🗿 <b>Your Shinobi Relics</b>:"]
    for relic in relics:
        lines.append(f"• <b>{relic['name']}</b> | 🔮 {relic['power']} | 💥 {relic['value']}")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")

async def shinobiartefact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    artefacts = get_user_artefacts(uid)

    if not artefacts:
        return await update.message.reply_text("🗝️ No artefacts found in your vault.")

    lines = ["🗝️ <b>Your Shinobi Artefacts</b>:"]
    for artefact in artefacts:
        lines.append(f"• <b>{artefact['name']}</b> — 🧠 {artefact['effect']}")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")

async def shinobiblessingvault(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    with get_conn() as conn:
        rows = conn.execute("SELECT blessing, received_at FROM blessings WHERE uid=?", (uid,)).fetchall()

    if not rows:
        return await update.message.reply_text("🙌 No blessings recorded yet.")

    lines = ["🙌 <b>Your Blessing Vault</b>:"]
    for blessing, ts in rows:
        date = time.strftime('%Y-%m-%d', time.localtime(ts))
        lines.append(f"• {blessing} — 🕒 {date}")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


async def shinobilegacy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    coins = get_balance(uid)
    karma = get_karma(uid)
    relics = get_user_relics(uid)
    artefacts = get_user_artefacts(uid)

    score = coins + karma + len(relics)*100 + len(artefacts)*150
    lines = [
        f"🧘 <b>Your Shinobi Legacy</b>",
        f"💰 Coins: {coins}",
        f"✨ Karma: {karma}",
        f"🗿 Relics: {len(relics)}",
        f"🗝️ Artefacts: {len(artefacts)}",
        f"\n🧠 <b>Legacy Score:</b> {score}"
    ]

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")

# === Timepass section  ===

async def sendheart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        return await update.message.reply_text("💌 Usage: /sendheart @username <your message>")

    target = context.args[0]
    message = " ".join(context.args[1:])
    if not target.startswith("@"):
        return await update.message.reply_text("💘 First argument must be an @username")

    # 🔍 Lookup UID
    with get_conn() as conn:
        row = conn.execute("SELECT uid FROM users WHERE username=?", (target[1:],)).fetchone()
        if not row:
            return await update.message.reply_text("❌ Target not found in bot database.")

    target_uid = row[0]
    sender_id = update.effective_user.id

    # 💾 Save pending message
    pending_heart[sender_id] = {
        "target_uid": target_uid,
        "target_username": target,
        "message": message
    }

    # 🏯 Fetch known groups
    with get_conn() as conn:
        groups = conn.execute("SELECT chat_id, title FROM known_groups").fetchall()

    if not groups:
        return await update.message.reply_text("📭 No groups found. Bot must be active in at least one group.")

    # 🧭 Build group selection buttons
    keyboard = []
    for chat_id, title in groups:
        keyboard.append([InlineKeyboardButton(f"📢 {title}", callback_data=f"heart_gc:{chat_id}")])
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="heart_cancel")])

    await update.message.reply_text(
        f"🩷 Choose a group to deliver your message for {target}:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def heart_confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id

    if uid not in pending_heart:
        return await query.edit_message_text("⚠️ No pending heart message.")

    data = pending_heart.pop(uid)
    msg = f"💌 <b>Someone left you a note:</b>\n🩷 \"{data['message']}\""

    if query.data.startswith("heart_gc:"):
        group_id = int(query.data.split(":")[1])
        try:
            await context.bot.send_message(
                chat_id=group_id,
                text=f"{data['target_username']} —\n{msg}",
                parse_mode="HTML"
            )
            await query.edit_message_text("📢 Heart posted in selected group 💘")
        except Exception as e:
            await query.edit_message_text("❌ Failed to send message to group.")
    else:
        await query.edit_message_text("❌ Heart canceled.")



async def propose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        return await update.message.reply_text("💍 Usage: /propose @username <your message>")

    target = context.args[0]
    message = " ".join(context.args[1:])
    if not target.startswith("@"):
        return await update.message.reply_text("💘 First argument must be an @username")

    # Lookup UID
    with get_conn() as conn:
        row = conn.execute("SELECT uid FROM users WHERE username=?", (target[1:],)).fetchone()
        if not row:
            return await update.message.reply_text("❌ Target not found in bot database.")

    target_uid = row[0]
    sender_id = update.effective_user.id
    sender_name = update.effective_user.first_name

    # Save pending proposal
    pending_proposal[target_uid] = {
        "sender_id": sender_id,
        "sender_name": sender_name,
        "message": message
    }

    keyboard = [
        [InlineKeyboardButton("💖 Accept", callback_data="proposal_accept"),
         InlineKeyboardButton("💔 Reject", callback_data="proposal_reject")]
    ]

    await context.bot.send_message(
        chat_id=target_uid,
        text=(
            f"💌 <b>@{update.effective_user.username}</b> has proposed to you:\n"
            f"🩷 \"{message}\""
        ),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

    await update.message.reply_text(f"✅ Proposal sent to {target} 💘")


async def proposal_response_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id

    if uid not in pending_proposal:
        return await query.edit_message_text("⚠️ No pending proposal.")

    data = pending_proposal.pop(uid)
    sender_name = data["sender_name"]

    if query.data == "proposal_accept":
        await query.edit_message_text(
            f"💖 <b>{query.from_user.first_name}</b> accepted the proposal from <b>{sender_name}</b>!\n"
            f"🌸 May your bond be stronger than any jutsu.",
            parse_mode="HTML"
        )
    else:
        await query.edit_message_text(
            f"💔 <b>{query.from_user.first_name}</b> rejected the proposal.\n"
            f"🥲 Better luck next time, shinobi.",
            parse_mode="HTML"
        )



# === Global Variables ===
equipped_spells = {}

# /start – Welcome message
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_user(update.effective_user.id, update.effective_user.username)
    await update.message.reply_text(
        "🃏 Welcome to UNO Reverse Duel Bot!\nStart with /earn, /draw or /spellbook!"
    )

# /balance – Show coin balance
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coins = get_balance(update.effective_user.id)
    await update.message.reply_text(f"💰 You have {coins} coins.")

# /earn – Claim daily coins
async def earn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not can_earn(uid):
        return await update.message.reply_text("🕒 Already claimed. Try again after 24 hours.")
    amount = random.randint(100, 300)
    update_balance(uid, amount)
    update_earn_time(uid)
    await update.message.reply_text(f"✅ You earned {amount} coins!")

# /party – Show recent active members
async def party(update: Update, context: ContextTypes.DEFAULT_TYPE):
    recent_users = get_recent_users(seconds=300)
    if not recent_users:
        return await update.message.reply_text("😴 No active members in the last 5 minutes.")
    mentions = " ".join(recent_users)
    await update.message.reply_text(f"🎉 Party time! Calling all active members:\n{mentions}", parse_mode="HTML")

# /karma – View your karma score
async def karma(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    k = get_karma(uid)
    formatted = format_karma(k)
    await update.message.reply_text(f"🌟 Your karma: {formatted}")


async def duelrank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    top_users = get_duel_rank(limit=10)
    if not top_users:
        return await update.message.reply_text("📭 No leaderboard data.")

    lines = ["🏅 <b>Duel Leaderboard</b>:"]
    for i, (uid, coins) in enumerate(top_users, start=1):
        lines.append(f"{i}. <b>{get_username(uid)}</b> — {coins} coins")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import ContextTypes
import time

# 🪙 Request Coins Command
async def request_coins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    requester = update.effective_user
    requester_id = requester.id

    if not context.args or len(context.args) < 1:
        return await update.message.reply_text("📦 Usage: /request <amount> [@username or UID] or reply to a message.")

    try:
        amount = int(context.args[0])
        if amount <= 0:
            return await update.message.reply_text("🚫 Amount must be positive.")
    except ValueError:
        return await update.message.reply_text("🚫 Amount must be a number.")

    # 🧑 Get target user ID
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        target_id = target_user.id
    elif len(context.args) >= 2:
        target = context.args[1]
        target_id = None
        if target.startswith("@"):
            username = target[1:]
            with get_conn() as conn:
                result = conn.execute("SELECT uid FROM users WHERE username=?", (username,)).fetchone()
                if result:
                    target_id = result[0]
        else:
            try:
                target_id = int(target)
            except ValueError:
                return await update.message.reply_text("🚫 Invalid UID.")
    else:
        return await update.message.reply_text("🧑 Specify who you're requesting from by replying or tagging.")

    target_name = get_username(target_id)
    await update.message.reply_text(
        f"📨 <b>{requester.full_name}</b> is requesting <b>{amount}</b> coins from <b>{target_name}</b>!",
        parse_mode="HTML"
    )

# ⚔️ Button Handler for Accept/Decline
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    await query.answer()
    data = query.data

    if data.startswith("accept:"):
        challenger_id, opponent_id = map(int, data.split(":")[1:])

        if user.id != opponent_id:
            return await query.edit_message_text("🚫 Only the challenged user can accept this duel.")

        context.chat_data["duel"] = {
            "players": [challenger_id, opponent_id],
            "turn": challenger_id,
            "hp": {challenger_id: 100, opponent_id: 100},
            "cards": {
                challenger_id: apply_rarity_bonus(get_random_card()),
                opponent_id: apply_rarity_bonus(get_random_card())
            }
        }
        await query.edit_message_text("✅ Challenge accepted! Duel begins!")
        await start_combat(update.effective_chat.id, context)

    elif data == "decline":
        await query.edit_message_text("❌ Challenge declined.")

# 🧙 Start Combat Phase
async def start_combat(chat_id, context: ContextTypes.DEFAULT_TYPE):
    buttons = [[
        InlineKeyboardButton("🗡️ Attack", callback_data="combat:attack"),
        InlineKeyboardButton("🛡️ Defend", callback_data="combat:defend")
    ]]
    await context.bot.send_message(
        chat_id=chat_id,
        text="🧙 The battle begins! Choose your action.",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# /send – Send coins to another user
async def send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender = update.effective_user
    sender_id = sender.id

    if not context.args or len(context.args) < 1:
        return await update.message.reply_text("📦 Usage: /send <amount> [@username or UID] or reply to a message.")

    try:
        amount = int(context.args[0])
        if amount <= 0:
            return await update.message.reply_text("🚫 Amount must be positive.")
    except ValueError:
        return await update.message.reply_text("🚫 Amount must be a number.")

    # 🧑 Detect recipient
    receiver_id = None
    receiver_name = "Unknown"

    if update.message.reply_to_message:
        receiver = update.message.reply_to_message.from_user
        receiver_id = receiver.id
        receiver_name = receiver.full_name
    elif len(context.args) >= 2:
        target = context.args[1]
        if target.startswith("@"):
            username = target[1:]
            with get_conn() as conn:
                result = conn.execute("SELECT uid FROM users WHERE username=?", (username,)).fetchone()
                if result:
                    receiver_id = result[0]
                    receiver_name = get_username(receiver_id)
        else:
            try:
                receiver_id = int(target)
                receiver_name = get_username(receiver_id)
            except ValueError:
                return await update.message.reply_text("🚫 Invalid UID.")
    else:
        return await update.message.reply_text("🧑 Specify a recipient by replying or using @username/UID.")

    if not receiver_id:
        return await update.message.reply_text("❌ Recipient not found.")

    # 💰 Check balance
    sender_balance = get_balance(sender_id)
    if sender_balance < amount:
        return await update.message.reply_text("🚫 Not enough coins to send.")

    # ✅ Transfer
    update_balance(sender_id, -amount)
    update_balance(receiver_id, amount)
    log_transfer(sender_id, receiver_id, amount)

    await update.message.reply_text(
        f"✅ <b>{sender.full_name}</b> sent <b>{amount}</b> coins to <b>{receiver_name}</b>!",
        parse_mode="HTML"
    )



async def adjustcoins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return await update.message.reply_text("⛔ Only admins can use this command.")

    if not context.args or len(context.args) < 2:
        return await update.message.reply_text("💰 Usage: /adjustcoins <@username or UID> <amount>")

    target = context.args[0]
    try:
        amount = int(context.args[1])
    except ValueError:
        return await update.message.reply_text("🚫 Amount must be a number.")

    uid = None
    if target.startswith("@"):
        username = target[1:]
        with get_conn() as conn:
            result = conn.execute("SELECT uid FROM users WHERE username=?", (username,)).fetchone()
            if result:
                uid = result[0]
    else:
        try:
            uid = int(target)
        except ValueError:
            return await update.message.reply_text("🚫 Invalid UID.")

    if not uid:
        return await update.message.reply_text("❌ User not found.")

    update_balance(uid, amount)
    new_balance = get_balance(uid)
    await update.message.reply_text(
        f"✅ Adjusted coins for <b>{get_username(uid)}</b>.\nNew Balance: <b>{new_balance}</b>",
        parse_mode="HTML"
    )

async def checkbalance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return await update.message.reply_text("⛔ Only admins can use this command.")

    if not context.args or len(context.args) < 1:
        return await update.message.reply_text("🧾 Usage: /checkbalance <@username or UID>")

    target = context.args[0]
    uid = None

    if target.startswith("@"):
        username = target[1:]
        with get_conn() as conn:
            result = conn.execute("SELECT uid FROM users WHERE username=?", (username,)).fetchone()
            if result:
                uid = result[0]
    else:
        try:
            uid = int(target)
        except ValueError:
            return await update.message.reply_text("🚫 Invalid UID.")

    if not uid:
        return await update.message.reply_text("❌ User not found.")

    coins = get_balance(uid)
    karma = get_karma(uid)
    username = get_username(uid)

    await update.message.reply_text(
        f"🧾 <b>{username}</b>\n💰 Coins: {coins}\n✨ Karma: {format_karma(karma)}",
        parse_mode="HTML"
    )

async def transferlog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return await update.message.reply_text("⛔ Only admins can view the transfer log.")

    logs = get_transfer_logs(limit=10)
    if not logs:
        return await update.message.reply_text("📭 No transfers found.")

    lines = ["📜 <b>Transfer Log</b>:"]
    for sender, receiver, amount, ts in logs:
        lines.append(f"💸 {get_username(sender)} → {get_username(receiver)}: {amount} coins")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")



# /give – Give coins to someone via reply or username
async def give(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender = update.effective_user
    sender_id = sender.id

    if not context.args or len(context.args) < 1:
        return await update.message.reply_text("📦 Usage: /give <amount> [@username or UID] or reply to a message.")

    try:
        amount = int(context.args[0])
        if amount <= 0:
            return await update.message.reply_text("🚫 Amount must be positive.")
    except ValueError:
        return await update.message.reply_text("🚫 Amount must be a number.")

    # 🧑 Detect recipient
    receiver_id = None
    if update.message.reply_to_message:
        receiver = update.message.reply_to_message.from_user
        receiver_id = receiver.id
    elif len(context.args) >= 2:
        target = context.args[1]
        if target.startswith("@"):
            username = target[1:]
            with get_conn() as conn:
                result = conn.execute("SELECT uid FROM users WHERE username=?", (username,)).fetchone()
                if result:
                    receiver_id = result[0]
        else:
            try:
                receiver_id = int(target)
            except ValueError:
                return await update.message.reply_text("🚫 Invalid UID.")
    else:
        return await update.message.reply_text("🧑 Specify a recipient by replying or using @username/UID.")

    if not receiver_id:
        return await update.message.reply_text("❌ Recipient not found.")

    # 💰 Check balance
    sender_balance = get_balance(sender_id)
    if sender_balance < amount:
        return await update.message.reply_text("🚫 Not enough coins to give.")

    # ✅ Transfer
    update_balance(sender_id, -amount)
    update_balance(receiver_id, amount)
    log_transfer(sender_id, receiver_id, amount)

    receiver_name = get_username(receiver_id)
    await update.message.reply_text(f"🎁 <b>{sender.full_name}</b> gave <b>{amount}</b> coins to <b>{receiver_name}</b>!", parse_mode="HTML")


import time
from card_utils import update_balance, get_username  # adjust if needed

# 🗣️ Honor Itachi every 5 minutes
async def itachi_listener(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.text:
        return

    text = msg.text.strip().lower()
    if text != "itachi is the best":
        return

    uid = msg.from_user.id
    now = int(time.time())
    cooldown = 300

    # first‐time or cooldown expired?
    last = last_itachi_reward.get(uid, 0)
    if now - last < cooldown:
        return await msg.reply_text(f"⏳ Try again in {cooldown - (now - last)}s.")

    # reward and record
    last_itachi_reward[uid] = now
    coins = 1000
    update_balance(uid, coins)
    await msg.reply_text(f"🩷 @{msg.from_user.username} earned {coins} coins for honoring Itachi!")


# /steal – Attempt to steal coins by replying
async def steal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("🕵️ Reply to someone to attempt stealing their coins.")

    thief = update.effective_user
    victim = update.message.reply_to_message.from_user

    thief_balance = get_balance(thief.id)
    victim_balance = get_balance(victim.id)

    if victim_balance < 50:
        return await update.message.reply_text("🚫 Victim doesn't have enough coins to steal.")

    stolen = random.randint(10, min(50, victim_balance))
    update_balance(victim.id, -stolen)
    update_balance(thief.id, stolen)

    await update.message.reply_text(f"🕵️ {thief.full_name} stole {stolen} coins from {victim.full_name}!")

# /reverse – Spend coins to "troll"
async def reverse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if get_balance(update.effective_user.id) < 25:
        return await update.message.reply_text("🚫 You need 25 coins to reverse.")
    target = context.args[0] if context.args else "@someone"
    update_balance(update.effective_user.id, -25)
    await update.message.reply_text(f"🔁 You reversed {target}'s move!")

# /draw – Pull a spell card
DRAW_COST = 100
DRAW_COOLDOWN = 60  # seconds

# Store last draw timestamps per user
last_draw_time = {}

async def draw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name or "Unknown"
    now = int(time.time())

    # ⏳ Check cooldown
    if uid in last_draw_time and (now - last_draw_time[uid]) < DRAW_COOLDOWN:
        remaining = DRAW_COOLDOWN - (now - last_draw_time[uid])
        return await update.message.reply_text(f"🕒 Please wait {remaining} seconds before drawing again.")

    # 🎲 Draw and boost card
    card = apply_rarity_bonus(get_random_card())
    cost = card.get("cost", DRAW_COST)
    balance = get_balance(uid)

    # 🚫 Check balance
    if balance < cost:
        return await update.message.reply_text(f"🚫 You need {cost} coins to draw this card. You have {balance}.")

    # 💸 Deduct coins and update draw time
    update_balance(uid, -cost)
    last_draw_time[uid] = now

    # 🗃️ Save to user_cards table
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
        conn.execute("""
            INSERT INTO user_cards (uid, file_id, name, power, value, rarity, drawn_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            uid,
            card.get("file_id"),
            card.get("name"),
            card.get("power"),
            card.get("value"),
            card.get("rarity"),
            now
        ))

    # 🎴 Build card preview
    card_text = (
        f"🎴 Card Drawn by {username}\n"
        f"🪄 Name: {card.get('name')}\n"
        f"🔥 Power: {card.get('power')}\n"
        f"💥 Value: {card.get('value')}\n"
        f"🎴 Rarity: {card.get('rarity')}\n"
        f"💸 Cost: {cost}\n"
        f"💰 Remaining Coins: {get_balance(uid)}"
    )

    file_id = card.get("file_id")
    if file_id:
        await update.message.reply_photo(photo=file_id, caption=card_text)
    else:
        await update.message.reply_text(card_text)


async def mycards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name

    with get_conn() as conn:
        rows = conn.execute("""
            SELECT name, power, value, rarity FROM user_cards
            WHERE uid=? ORDER BY drawn_at DESC LIMIT 20
        """, (uid,)).fetchall()

    if not rows:
        return await update.message.reply_text(
            f"📭 <b>{username}</b>, you haven’t drawn any cards yet.",
            parse_mode="HTML"
        )

    lines = [f"🃏 <b>{username}'s Cards</b>:"]
    for name, power, value, rarity in rows:
        lines.append(f"• <b>{name}</b> | 🔮 {power} | 💥 {value} | 🎴 {rarity}")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")



async def cardlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cards = list_all_cards()
    if not cards:
        return await update.message.reply_text("📭 No cards available in the bot.")

    lines = ["📜 <b>Available Cards</b>:"]
    for i, card in enumerate(cards, start=1):
        name = card.get("name", "Unknown")
        power = card.get("power", "Unknown")
        value = card.get("value", 0)
        rarity = card.get("rarity", "Common")
        lines.append(f"{i}. <b>{name}</b> | 🔮 {power} | 💥 {value} | 🎴 {rarity}")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")




# /top – Leaderboard by coins
async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Fetch all users and their balances
    uids = get_all_user_ids()
    if not uids:
        return await update.message.reply_text("📭 No users found.")

    # Build a list of (uid, balance) and sort descending
    leaderboard = sorted(
        [(uid, get_balance(uid)) for uid in uids],
        key=lambda x: x[1],
        reverse=True
    )[:10]  # top 10

    if not leaderboard or all(balance == 0 for _, balance in leaderboard):
        return await update.message.reply_text("📭 No one has coins yet.")

    # Format the leaderboard
    lines = ["🏆 <b>Top Coin Holders</b>:"]
    for rank, (uid, balance) in enumerate(leaderboard, start=1):
        username = get_username(uid)
        lines.append(f"{rank}. <b>{username}</b> — 💰 {balance} coins")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


async def welcome_farewell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_change = update.chat_member
    user = status_change.new_chat_member.user
    status = status_change.new_chat_member.status

    if status == ChatMemberStatus.MEMBER:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"👋 Welcome <b>{user.full_name}</b> to the group!",
            parse_mode="HTML"
        )
    elif status in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED]:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"👋 <b>{user.full_name}</b> has left the group.",
            parse_mode="HTML"
        )

async def challenge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("🔁 Reply to someone’s message to challenge them.")

    challenger = update.message.from_user
    opponent = update.message.reply_to_message.from_user

    # Save IDs in callback
    keyboard = [[
        InlineKeyboardButton("✅ Accept", callback_data=f"accept:{challenger.id}:{opponent.id}"),
        InlineKeyboardButton("❌ Decline", callback_data="decline")
    ]]

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"⚔️ <b>{opponent.full_name}</b>, you've been challenged by <b>{challenger.full_name}</b>!",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def start_combat(chat_id, context: ContextTypes.DEFAULT_TYPE):
    buttons = [[
        InlineKeyboardButton("🗡️ Attack", callback_data="combat:attack"),
        InlineKeyboardButton("🛡️ Defend", callback_data="combat:defend")
    ]]
    await context.bot.send_message(
        chat_id=chat_id,
        text="🧙 The battle begins! Choose your action.",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

def calculate_damage(card1, card2, action):
    base = card1.get("value", 0)
    defense = card2.get("value", 0)
    if action == "attack":
        return max(10, base - defense // 2)
    elif action == "defend":
        return max(5, base // 2)
    return 0

async def combat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    action = query.data.split(":")[1]

    duel = context.chat_data.get("duel")
    if not duel or user.id != duel["turn"]:
        return await query.edit_message_text("❌ Not your turn!")

    attacker = user.id
    defender = [uid for uid in duel["players"] if uid != attacker][0]
    damage = calculate_damage(duel["cards"][attacker], duel["cards"][defender], action)

    duel["hp"][defender] -= damage
    duel["turn"] = defender

    if duel["hp"][defender] <= 0:
        await query.edit_message_text(f"🏆 <b>{user.full_name}</b> wins the duel!", parse_mode="HTML")
        context.chat_data.pop("duel")
        return

    await query.edit_message_text(
        text=f"🗡️ <b>{user.full_name}</b> used {action.upper()} — dealt {damage} damage!\n\n"
             f"⚔️ <b>{duel['hp'][attacker]}HP</b> vs <b>{duel['hp'][defender]}HP</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🗡️ Attack", callback_data="combat:attack"),
            InlineKeyboardButton("🛡️ Defend", callback_data="combat:defend")
        ]])
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    await query.answer()
    data = query.data

    if data.startswith("accept:"):
        challenger_id, opponent_id = map(int, data.split(":")[1:])
        
        if user.id != opponent_id:
            return await query.edit_message_text("🚫 Only the challenged user can accept this duel.")

        # Proceed with duel setup...

async def spellbook(update: Update, context: ContextTypes.DEFAULT_TYPE):
    wins, _, _ = get_duel_rank(update.effective_user.username)
    if wins < 25:
        return await update.message.reply_text("🔒 Prestige unlocks after 25 wins.")
    spells = get_spell_shop()
    msg = "📖 Prestige Spellbook:\n" + "\n".join([
        f"- {s['power'].title()} | {s['rarity']} | {s['value']} coins"
        for s in spells
    ])
    await update.message.reply_text(msg)

async def castspell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("🧙 Usage: /castspell powername")
    power = context.args[0].lower()
    wins, _, _ = get_duel_rank(update.effective_user.username)
    if wins < 25:
        return await update.message.reply_text("🔒 You need 25 wins to cast Prestige spells.")
    spell = get_spell_by_power(power)
    if not spell:
        return await update.message.reply_text("❌ No such Prestige spell: " + power)
    update_balance(update.effective_user.id, spell["value"])
    await update.message.reply_text(
        f"🔮 Casted {power.title()}!\n💥 Effect: {spell['value']} coins\n🎖️ Rarity: {spell['rarity'].title()}",
        parse_mode="Markdown"
    )

async def cardvault(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return await update.message.reply_text("⛔ Only admins can access the card vault.")

    cards = list_all_cards()
    if not cards:
        return await update.message.reply_text("📭 No cards found.")

    for card in cards:
        name = card.get("name", "Unknown")
        power = card.get("power", "Unknown")
        value = card.get("value", 0)
        rarity = card.get("rarity", "Common")

        text = (
            f"🃏 <b>{name}</b>\n"
            f"🔮 Power: {power}\n"
            f"💥 Value: {value}\n"
            f"🎴 Rarity: {rarity}"
        )

        keyboard = [[InlineKeyboardButton("🗑️ Delete", callback_data=f"removecard:{name}")]]
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))



async def deletecard_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    await query.answer()

    if uid not in ADMIN_IDS:
        return await query.edit_message_text("⛔ Only admins can delete cards.")

    if query.data.startswith("removecard:"):
        card_name = query.data.split(":", 1)[1]
        success = remove_card_by_name(card_name)
        if success:
            await query.edit_message_text(f"✅ Card '<b>{card_name}</b>' removed from the bot.", parse_mode="HTML")
        else:
            await query.edit_message_text(f"⚠️ Failed to remove card '<b>{card_name}</b>'. Not found.", parse_mode="HTML")



async def deletecardbyindex(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return await update.message.reply_text("⛔ Only admins can delete cards.")

    if not context.args:
        return await update.message.reply_text("🗑️ Usage: /deletecardbyindex <card_number>")

    try:
        index = int(context.args[0]) - 1  # Convert to 0-based index
    except ValueError:
        return await update.message.reply_text("🚫 Please enter a valid number.")

    from card_utils import remove_card_by_index
    name = remove_card_by_index(index)

    if name:
        await update.message.reply_text(f"✅ Card <b>{name}</b> deleted successfully.", parse_mode="HTML")
    else:
        await update.message.reply_text("⚠️ Card not found or deletion failed.")


async def deletecardbyindex(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return await update.message.reply_text("⛔ Only admins can delete cards.")

    if not context.args:
        return await update.message.reply_text("🗑️ Usage: /deletecardbyindex <card_number>")

    try:
        index = int(context.args[0]) - 1  # Convert to 0-based index
    except ValueError:
        return await update.message.reply_text("🚫 Please enter a valid number.")

    from card_utils import remove_card_by_index
    name = remove_card_by_index(index)

    if name:
        await update.message.reply_text(f"✅ Card <b>{name}</b> deleted successfully.", parse_mode="HTML")
    else:
        await update.message.reply_text("⚠️ Card not found or deletion failed.")



async def deletebyname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return await update.message.reply_text("⛔ Only admins can use this command.")

    if not context.args:
        return await update.message.reply_text("🗑️ Usage: /deletebyname <card_name>")

    card_name = " ".join(context.args).strip()
    success = remove_card_by_name(card_name)
    
    if success:
        await update.message.reply_text(f"✅ Card '<b>{card_name}</b>' deleted from the database.", parse_mode="HTML")
    else:
        await update.message.reply_text(f"⚠️ Card '<b>{card_name}</b>' not found or deletion failed.", parse_mode="HTML")




async def equipspell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("🧙 Usage: /equipspell burn")
    power = context.args[0].lower()
    equipped_spells[update.effective_user.id] = power
    await update.message.reply_text(f"✅ Equipped spell: {power.title()}")

async def unequipspell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    equipped_spells.pop(update.effective_user.id, None)
    await update.message.reply_text("🧹 Spell unequipped.")


async def uploadcard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg.reply_to_message or not msg.reply_to_message.photo:
        return await msg.reply_text("📸 Reply to a photo message to upload a card.")

    caption = msg.reply_to_message.caption
    if not caption or "|" not in caption:
        return await msg.reply_text("📝 Caption must be in format:\nname | power | value | rarity | cost")

    parts = [p.strip() for p in caption.split("|")]
    if len(parts) != 5:
        return await msg.reply_text("🚫 Invalid format. Use:\nname | power | value | rarity | cost")

    name, power, value, rarity, cost = parts
    try:
        value = int(value)
        cost = int(cost)
    except ValueError:
        return await msg.reply_text("🚫 Value and cost must be numbers.")

    photo = msg.reply_to_message.photo[-1]
    file_id = photo.file_id

    card = {
        "name": name,
        "power": power,
        "value": value,
        "rarity": rarity.lower(),
        "cost": cost,
        "file_id": file_id
    }

    success = add_card(file_id, json.dumps(card))
    if success:
        await msg.reply_text(f"✅ Card '{name}' uploaded successfully!")
    else:
        await msg.reply_text("⚠️ Failed to upload card.")

async def deletecard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("🗑️ Usage: /deletecard <file_id>")
    file_id = context.args[0]
    remove_card(file_id)
    await update.message.reply_text(f"✅ Card with file_id {file_id} deleted.")

async def editcard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        return await update.message.reply_text("✏️ Usage: /editcard <file_id> <new_json>")
    file_id = context.args[0]
    new_json = " ".join(context.args[1:])
    try:
        json.loads(new_json)
        add_card(file_id, new_json)
        await update.message.reply_text("✅ Card updated.")
    except:
        await update.message.reply_text("🚫 Invalid JSON format.")



async def debugvault(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cards = list_all_cards()
    total = len(cards)
    lines = [f"📦 Found {total} cards in vault."]
    for c in cards:
        lines.append(f"• {c.get('name')} | 🎴 {c.get('rarity')} | 💥 {c.get('value')}")
    await update.message.reply_text("\n".join(lines), parse_mode="HTML")



async def adminpanel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return await update.message.reply_text("⛔ Only admins can access the panel.")

    buttons = [
        [InlineKeyboardButton("💰 Adjust Coins", callback_data="adjustcoins")],
        [InlineKeyboardButton("🔍 Check Balance", callback_data="checkbalance")],
        [InlineKeyboardButton("📜 Transfer Log", callback_data="transferlog")],
        [InlineKeyboardButton("🏅 Leaderboard", callback_data="leaderboard")],
        [InlineKeyboardButton("🃏 Manage Cards", callback_data="managecards")],
    ]
    markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("🛠️ Admin Control Panel:", reply_markup=markup)


async def getfileid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        return await update.message.reply_text("📸 Reply to a photo to get its file ID.")

    photo = update.message.reply_to_message.photo[-1]
    await update.message.reply_text(f"🆔 File ID: <code>{photo.file_id}</code>", parse_mode="HTML")


async def panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id

    if uid not in ADMIN_IDS:
        return await query.edit_message_text("⛔ Admin access only.")

    data = query.data

    if data == "adjustcoins":
        return await query.edit_message_text("💰 Use /adjustcoins <@username or UID> <amount>")

    elif data == "checkbalance":
        return await query.edit_message_text("🔍 Use /checkbalance <@username or UID>")

    elif data == "transferlog":
        logs = get_transfer_logs(limit=10)
        if not logs:
            return await query.edit_message_text("📭 No transfers found.")
        lines = ["📜 <b>Transfer Log</b>:"]
        for sender, receiver, amount, ts in logs:
            lines.append(f"💸 {get_username(sender)} → {get_username(receiver)}: {amount} coins")
        await query.edit_message_text("\n".join(lines), parse_mode="HTML")

    elif data == "leaderboard":
        top_users = get_duel_rank(limit=10)
        if not top_users:
            return await query.edit_message_text("📭 No leaderboard data.")
        lines = ["🏅 <b>Leaderboard</b>:"]
        for i, (uid, coins) in enumerate(top_users, start=1):
            lines.append(f"{i}. <b>{get_username(uid)}</b> — {coins} coins")
        await query.edit_message_text("\n".join(lines), parse_mode="HTML")

    elif data == "managecards":
        cards = list_all_cards()
        if not cards:
            return await query.edit_message_text("📭 No cards found.")
        lines = ["🃏 <b>Card Vault</b>:"]
        for i, card in enumerate(cards, start=1):
            lines.append(f"{i}. <b>{card['name']}</b> | {card['power']} | {card['value']} | {card['rarity']}")
        await query.edit_message_text("\n".join(lines), parse_mode="HTML")


KARMA_TRIGGERS = ["+1", "++", "+karma", "👍", "👍🏼", "✨"]

async def karma_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.reply_to_message:
        return

    text = msg.text.strip().lower()
    giver = msg.from_user
    receiver = msg.reply_to_message.from_user

    if giver.id == receiver.id:
        return await msg.reply_text("🫣 You can't karma boost yourself.")

    track_user(giver.id, giver.username)
    track_user(receiver.id, receiver.username)

    karma_boost = 0
    if any(trigger in text for trigger in KARMA_TRIGGERS):
        karma_boost = 1
    elif "itachi is best" in text:
        karma_boost = 5

    if karma_boost == 0:
        return

    conn = get_conn()
    conn.execute("UPDATE users SET karma = karma + ? WHERE uid = ?", (karma_boost, receiver.id))
    conn.commit()

    karma = get_karma(receiver.id)
    await msg.reply_text(
        f"🌟 <b>{receiver.full_name}</b> gained <b>{karma_boost}</b> karma!\nTotal Karma: <b>{format_karma(karma)}</b>",
        parse_mode="HTML"
    )


async def activity_tracker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.from_user:
        user = update.message.from_user
        track_user(user.id, user.username)

        # 🧠 Track group if message is from a group or supergroup
        if update.effective_chat and update.effective_chat.type in ["group", "supergroup"]:
            chat_id = update.effective_chat.id
            title = update.effective_chat.title or "Unnamed Group"
            track_group(chat_id, title)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.error("⚠️ Exception while handling update:", exc_info=context.error)
    try:
        if update and hasattr(update, "message") and update.message:
            await update.message.reply_text("⚠️ Something went wrong. The devs have been notified.")
        elif update and hasattr(update, "callback_query") and update.callback_query:
            await update.callback_query.message.edit_text("⚠️ Something went wrong. The devs have been notified.")
        else:
            chat_id = getattr(update, "effective_chat", None)
            if chat_id:
                await context.bot.send_message(chat_id.id, "⚠️ Something went wrong.")
    except Exception as e:
        logging.error("🧨 Failed to send error message:", exc_info=e)


# === Bot Setup ===
app = ApplicationBuilder().token(BOT_TOKEN).build()

# === Command Registry ===
commands = {
    "start": start,
    "help": help_command,
    "balance": balance,
    "earn": earn,
    "reverse": reverse,
    "draw": draw,
    "mycards": mycards,
    "steal": steal,
    "send": send,
    "give": give,
    "challenge": challenge,
    "request": request_coins,
    "top": top,
    "spellbook": spellbook,
    "castspell": castspell,
    "equipspell": equipspell,
    "unequipspell": unequipspell,
    "uploadcard": uploadcard,
    "deletecard": deletecard,
    "deletebyname": deletebyname,
    "deletecardbyindex": deletecardbyindex,
    "deletebyindex": deletebyindex,
    "editcard": editcard,
    "adjustcoins": adjustcoins,
    "checkbalance": checkbalance,
    "transferlog": transferlog,
    "duelrank": duelrank,
    "cardvault": cardvault,
    "cardlist": cardlist,
    "party": party,
    "karma": karma,
    "adminpanel": adminpanel,
    "assetmarket": assetmarket,
    "buyasset": buyasset,
    "myassets": myassets,
    "collectincome": collectincome,
    "sellasset": sellasset,
    "mintasset": mintasset,
    "investrank": investrank,
    "assetinfo": assetinfo,
    "assettrend": assettrend,
    "fluctuateprices": fluctuateprices,
    "auditvault": auditvault,
    "assetshare": assetshare,
    "bankstats": bankstats,
    "assetcompare": assetcompare,
    "assetlore": assetlore,
    "flashsale": flashsale,
    "runbankengine": runbankengine,
    "achievements": achievements,
    "assettitle": assettitle,
    "questbook": questbook,
    "getfileid": getfileid,
    "groupgoal": groupgoal,
    "dailymission": dailymission,
    "claimstreak": claimstreak,
    "profilecard": profilecard,
    "bossfight": bossfight,
    "clangoal": clangoal,
    "invite": invite,
    "duelnews": duelnews,
    "banknews": banknews,
    "npcvisit": npcvisit,
    "cardstats": cardstats,
    "prestigevault": prestigevault,
    "shinobiquiz": shinobiquiz,
    "karmahall": karmahall,
    "duelbadge": duelbadge,
    "shinobishop": shinobishop,
    "buyitem": buyitem,
    "shinobititle": shinobititle,
    "karmaquiz": karmaquiz,
    "shinobirank": shinobirank,
    "shinobibadge": shinobibadge,
    "shinobichest": shinobichest,
    "shinobiarena": shinobiarena,
    "shinobitask": shinobitask,
    "shinobiblessing": shinobiblessing,
    "shinobiforge": shinobiforge,
    "shinobitrade": shinobitrade,
    "shinobialtar": shinobialtar,
    "shinobimarket": shinobimarket,
    "shinobispell": shinobispell,
    "shinobitomb": shinobitomb,
    "equipspell": equipspell,
    "marketbuy": marketbuy,
    "tombstats": tombstats,
    "shinobifusion": shinobifusion,
    "shinobibattle": shinobibattle,
    "shinobirelic": shinobirelic,
    "shinobiartefact": shinobiartefact,
    "shinobiblessingvault": shinobiblessingvault,
    "shinobilegacy": shinobilegacy,
    "sendheart": sendheart,
    "debugvault": debugvault
   


}

# === Register Commands ===
for cmd, func in commands.items():
    app.add_handler(CommandHandler(cmd, func))

# === Button & Callback Handlers ===
app.add_handler(CallbackQueryHandler(heart_confirm_handler, pattern="^heart_"))
app.add_handler(CallbackQueryHandler(deletecard_callback, pattern="^removecard:"))
app.add_handler(CallbackQueryHandler(button_handler, pattern="^accept:|^decline$"))
app.add_handler(CallbackQueryHandler(combat_handler, pattern="^combat"))
app.add_handler(CallbackQueryHandler(panel_callback))
app.add_handler(CommandHandler("propose", propose))
app.add_handler(CallbackQueryHandler(proposal_response_handler, pattern="^proposal_"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, itachi_listener))

app.add_handler(CommandHandler("deletebyindex", deletebyindex))

# — Register the new help command —
app.add_handler(CommandHandler("help", help_command))




# General fallback last
app.add_handler(CallbackQueryHandler(button_handler))


# === Karma System ===
app.add_handler(MessageHandler(filters.TEXT & filters.REPLY, karma_handler))

# === Activity Tracker ===
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, activity_tracker))

# === Welcome & Farewell ===
app.add_handler(ChatMemberHandler(welcome_farewell, ChatMemberHandler.CHAT_MEMBER))

# === Error Handler ===
app.add_error_handler(error_handler)


if __name__ == "__main__":
    print("✅ UNO Reverse Bot is running...")
    app.run_polling()


