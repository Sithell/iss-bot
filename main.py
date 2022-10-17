#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging
import requests
import os


from telegram import KeyboardButton, ReplyKeyboardMarkup, Update, User
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

HELP_MSG = """Команды:
/help - показать это сообщение
/status - текущее положение МКС
"""

TOKEN = os.getenv('TELEGRAM_TOKEN')

def start(update, context):
    update.message.reply_text(HELP_MSG)


def help(update, context):
    update.message.reply_text(HELP_MSG)


def echo(update: Update, context):
    update.message.reply_text(HELP_MSG)


def status(update: Update, context):
    r = requests.get('http://api.open-notify.org/iss-now.json')
    longitude = r.json()["iss_position"]["longitude"]
    latitude = r.json()["iss_position"]["latitude"]
    update.message.reply_location(latitude, longitude)
    update.message.reply_text(f"Долгота: {longitude}, широта: {latitude}")


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

