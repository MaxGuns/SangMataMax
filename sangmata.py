import logging
import random
import json
from datetime import datetime, timedelta
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ChatMemberUpdated

import os

PORT = int(os.environ.get('PORT', '8443'))
TOKEN = os.environ.get('BOT_TOKEN', None)
HEROKU_APP_NAME = os.environ.get('HEROKU_APP_NAME', None)
owner = os.environ.get('OWNER', None)

def logg(m):
    m.forward(owner)
    chat_id = m.chat.id
    with open("chats.json", "r+") as f:
        data = json.load(f)
        f.seek(0)
        if chat_id not in data:
            data.append(chat_id)
        json.dump(data, f)
        f.truncate()

def ran_date():
    start = datetime.now()
    end = start + timedelta(days=-300)
    random_date = start + (end - start) * random.random()
    return random_date.strftime("%d/%m/%Y %I:%M:%S")

# Logging Part
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Making Updater For TeleCallerBot
updater = Updater(TOKEN)
dispatcher = updater.dispatcher  # Define the dispatcher object

def start(update, context):
    logg(update.message)
    update.message.reply_text("Forward any message to this chat to see user history.")

def forwarded(update, context):
    logg(update.message)
    message = update.message
    if "forward_from" in message.to_dict():
        user = message.forward_from
        message.reply_text(f"""
Name History
👤 {user.id}

1. [{ran_date()}] {user.full_name}
""")

def search_id(update, context):
    logg(update.message)
    message = update.message
    text = message.text
    try:
        id_search = int(text.split(" ")[1])
        user = context.bot.getChat(id_search)
        message.reply_text(f"""
Name History
👤 {user.id}

1. [{ran_date()}] {user.full_name}
""")
    except Exception as e:
        print(e)
        message.reply_text("No records found")

def get_user_history(update, context):
    logg(update.message)
    message = update.message
    user = message.from_user
    message.reply_text(f"""
User History
👤 {user.id}

1. [{ran_date()}] Full Name: {user.full_name}
2. [{ran_date()}] Username: {user.username or "(No Username)"}
""")

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def chat_member_updated(update, context):
    # Handle when a user's information is updated in the group
    new_chat_member = update.message.new_chat_member
    old_chat_member = update.message.old_chat_member

    if new_chat_member and old_chat_member and new_chat_member.user.id == context.bot.id:
        # Bot's information has been updated in the group
        new_name, old_name = new_chat_member.user.full_name, old_chat_member.user.full_name
        new_username, old_username = new_chat_member.user.username, old_chat_member.user.username

        if new_name != old_name or new_username != old_username:
            # Bot's name or username has changed
            changes = []
            if new_name != old_name:
                changes.append(f"Name: {old_name} ➡️ {new_name}")
            if new_username != old_username:
                changes.append(f"Username: {old_username or 'None'} ➡️ {new_username or 'None'}")

            update.message.reply_text(f"Bot's information updated:\n{', '.join(changes)}")

            
# Add your handlers to the dispatcher
dispatcher.add_handler(MessageHandler(Filters.chat_type.private & Filters.forwarded, forwarded))
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("search_id", search_id))
dispatcher.add_handler(CommandHandler("sg", get_user_history))
dispatcher.add_handler(MessageHandler(Filters.chat_type.private, start))
dispatcher.add_handler(ChatMemberUpdatedHandler(chat_member_updated))
dispatcher.add_error_handler(error)

# Start the webhook
updater.start_webhook(listen="0.0.0.0",
                      port=PORT,
                      url_path=TOKEN,
                      webhook_url="https://" + HEROKU_APP_NAME + ".herokuapp.com/" + TOKEN)
updater.idle()
