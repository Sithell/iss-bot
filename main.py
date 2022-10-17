#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging
import threading
import time

import requests
import os

from telegram import KeyboardButton, ReplyKeyboardMarkup, Update, User, Location, Bot, Message
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

HELP_MSG = """Команды:
/help - показать это сообщение
/status - текущее положение МКС
"""

TOKEN = os.getenv('TELEGRAM_TOKEN')
locations: dict[int, (Message, Message)] = {}


def start(update, context):
    update.message.reply_text(HELP_MSG)


def help(update, context):
    update.message.reply_text(HELP_MSG)


def echo(update: Update, context):
    update.message.reply_text(HELP_MSG)


def status(update: Update, context: CallbackContext):
    logger.info(update.message.chat_id)
    global locations
    r = requests.get('http://api.open-notify.org/iss-now.json')
    longitude = r.json()["iss_position"]["longitude"]
    latitude = r.json()["iss_position"]["latitude"]
    location_msg = update.message.reply_location(latitude, longitude, live_period=180)
    text_msg = update.message.reply_text(f"Долгота: {longitude}, широта: {latitude}")
    locations[update.message.chat_id] = (location_msg, text_msg)


def update_location(bot: Bot):
    time.sleep(2)
    r = requests.get('http://api.open-notify.org/iss-now.json')
    longitude = r.json()["iss_position"]["longitude"]
    latitude = r.json()["iss_position"]["latitude"]
    location_msg: Message
    text_msg: Message
    for chat_id, (location_msg, text_msg) in locations.items():
        bot.edit_message_text(chat_id=chat_id, message_id=text_msg.message_id,
                              text=f"Долгота: {longitude}, широта: {latitude}")
        bot.edit_message_live_location(chat_id=chat_id, message_id=location_msg.message_id, longitude=longitude,
                                       latitude=latitude)

    logger.info("BEEP")

    update_location(bot)


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    global bot
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_error_handler(error)

    live_location = threading.Thread(target=update_location, args=(updater.bot,), daemon=True)
    updater.start_polling()
    live_location.start()
    updater.idle()


if __name__ == '__main__':
    main()

