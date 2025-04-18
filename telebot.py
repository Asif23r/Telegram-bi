from telegram import Update, Bot, ParseMode from telegram.ext import Updater, CommandHandler, CallbackContext import json import os

TOKEN = "YOUR_BOT_TOKEN_HERE" DB_FILE = "db.json" OWNER_ID = 123456789  # Replace with your Telegram ID

Initialize DB

if not os.path.exists(DB_FILE): with open(DB_FILE, 'w') as f: json.dump({"users": {}, "admins": [OWNER_ID], "requests": []}, f)

def load_db(): with open(DB_FILE, 'r') as f: return json.load(f)

def save_db(db): with open(DB_FILE, 'w') as f: json.dump(db, f, indent=2)

def is_admin(user_id): db = load_db() return user_id in db["admins"] or user_id == OWNER_ID

def start(update: Update, context: CallbackContext): user = update.effective_user db = load_db() if str(user.id) not in db['users']: db['users'][str(user.id)] = {"points": 0.0, "refers": []} save_db(db) update.message.reply_text(f"👋 Welcome {user.first_name} to the Bot!\n🎯 Use /refer <user_id> to invite and earn points.")

def refer(update: Update, context: CallbackContext): db = load_db() referrer = update.effective_user.id if len(context.args) != 1: update.message.reply_text("❌ Usage: /refer <user_id>") return try: referred_id = int(context.args[0]) except: update.message.reply_text("⚠️ Invalid user ID!") return if str(referred_id) not in db['users']: update.message.reply_text("❌ Referred user not found.") return # Add 0.4 point to referred user db['users'][str(referred_id)]['points'] += 0.4 db['users'][str(referred_id)]['refers'].append(referrer) save_db(db) update.message.reply_text("✅ Refer successful! Receiver got 0.4 point.")

def points(update: Update, context: CallbackContext): db = load_db() user_id = str(update.effective_user.id) pts = db['users'].get(user_id, {}).get("points", 0.0) update.message.reply_text(f"💸 You have {pts:.1f} point(s).")

def buy(update: Update, context: CallbackContext): db = load_db() user_id = str(update.effective_user.id) pts = db['users'].get(user_id, {}).get("points", 0.0) if pts >= 1.0: if user_id in db['requests']: update.message.reply_text("⏳ Your request is already sent. Please wait.") return db['requests'].append(user_id) save_db(db) update.message.reply_text("🛒 Buy request sent to admin.") for admin_id in db['admins'] + [OWNER_ID]: context.bot.send_message(admin_id, f"🔔 User {user_id} has requested to buy an account. Use /verify {user_id} to approve.") else: update.message.reply_text("❌ Not enough points to buy. Earn points using /refer.")

def verify(update: Update, context: CallbackContext): if not is_admin(update.effective_user.id): update.message.reply_text("❌ Only admins can use this command.") return db = load_db() if len(context.args) != 1: update.message.reply_text("Usage: /verify <user_id>") return user_id = context.args[0] if user_id not in db['requests']: update.message.reply_text("⚠️ No pending request for this user.") return if db['users'][user_id]['points'] < 1.0: update.message.reply_text("❌ User doesn't have enough points.") return db['users'][user_id]['points'] -= 1.0 db['requests'].remove(user_id) save_db(db) context.bot.send_message(user_id, "✅ Your request is verified. Here is your account detail: (send manually)") update.message.reply_text("🎯 Verified and notified user.")

def addadmin(update: Update, context: CallbackContext): if update.effective_user.id != OWNER_ID: return db = load_db() if len(context.args) != 1: update.message.reply_text("Usage: /addadmin <user_id>") return uid = int(context.args[0]) if uid not in db['admins']: db['admins'].append(uid) save_db(db) update.message.reply_text("✅ Admin added.")

def removeadmin(update: Update, context: CallbackContext): if update.effective_user.id != OWNER_ID: return db = load_db() if len(context.args) != 1: update.message.reply_text("Usage: /removeadmin <user_id>") return uid = int(context.args[0]) if uid in db['admins']: db['admins'].remove(uid) save_db(db) update.message.reply_text("❌ Admin removed.")

def main(): updater = Updater(TOKEN) dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("refer", refer))
dp.add_handler(CommandHandler("points", points))
dp.add_handler(CommandHandler("buy", buy))
dp.add_handler(CommandHandler("verify", verify))
dp.add_handler(CommandHandler("addadmin", addadmin))
dp.add_handler(CommandHandler("removeadmin", removeadmin))

updater.start_polling()
updater.idle()

if name == 'main': main()

