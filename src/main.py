import telegram.ext
import os
import logging
import database as db
import importlib

from telegram import Update
from telegram.ext import  Updater, Filters, CallbackContext

StartText=''
Version_Code = 'v13.8.1'
Home_Url = 'https://github.com/metromy/mytelegram_bot_v13.8'

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

GENDER, PHOTO, LOCATION, BIO = range(4)

PATH = os.path.dirname(os.path.realpath(__file__)) + '/'

CONFIG = db.read("config")

Modules = []

def reload_start():
    global StartText
    StartText = open(PATH + 'start.txt', 'r', encoding='utf-8').read()
    if StartText: print("Start Text Loaded")

def reload_modules():
    for key in CONFIG['Modules'].keys():
        Modules.append(importlib.import_module(key))
        print("Module {0} {1} Loaded".format(key, CONFIG['Modules'][key]))

def process_command(update: Update, context: CallbackContext):
    if update.channel_post: return
    command = update.message.text[1:]
    if command == 'start':
        update.message.reply_text(StartText)
        return
    elif command == 'version':
        update.message.reply_text(text='Telegram Bot\n' + Version_Code + '\n' + Home_Url)
        return
    elif command == 'reload' and update.message.from_user.id == CONFIG['Admin']:
        reload_start()
        reload_modules()
        update.message.reply_text(text="已重新加载")
        return
    else: 
        for mod in Modules: mod.process_command(update, context)

def process_msg(update: Update, context: CallbackContext):
    if update.channel_post: return
    for mod in Modules: mod.process_msg(update, context)

def process_callback(update: Update, context: CallbackContext):
    if update.channel_post: return
    for mod in Modules: mod.process_callback(update, context)
    
def main():
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(token=CONFIG['Token'])
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    me = updater.bot.get_me()
    CONFIG['ID'] = me.id
    CONFIG['Username'] = '@' + me.username
    db.save("config", CONFIG)

    print('Starting... (ID: ' + str(CONFIG['ID']) + ', Username: ' + CONFIG['Username'] + ')')

    reload_start()
    reload_modules()

    dispatcher.add_handler(telegram.ext.MessageHandler(Filters.command, process_command))

    dispatcher.add_handler(telegram.ext.MessageHandler(Filters.photo | Filters.video | Filters.text, process_msg))

    dispatcher.add_handler(telegram.ext.CallbackQueryHandler(process_callback))

    updater.start_polling()
    print('Started')
    updater.idle()
    print('Stopped.')

if __name__ == '__main__':
    main()
