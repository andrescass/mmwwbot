#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Miralos Morfarse Spaming bot
"""

import logging
import os
import random
import sys
import json
import requests
from datetime import datetime, timedelta
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

spam_msgs = ["Ante la duda, siempre Rodri", "Por antecedentes la mala es Mar", "Anton está muy callado, es sospechoso", 
"Si no hay muertes hay que linchar a Juan"]

# Getting mode, so we could define run function for local and Heroku setup
mode = os.getenv("MODE")
# mode = "dev"
TOKEN = os.getenv("TOKEN")
if mode == "dev":
    TOKEN = "1300813089:AAFv3PzPeVi33JiZKySyWdiwwiBJvPSUnSw"
    def run(updater):
        updater.start_polling()
elif mode == "prod":
    def run(updater):
        PORT = int(os.environ.get("PORT", "8443"))
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
        # Code from https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks#heroku
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=TOKEN)
        updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))
else:
    logger.error("No MODE  specified!")
    sys.exit(1)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    update.message.reply_text('Buenas buenas, lobites')

def random_spam(context):
    job = context.job
    r = random.randint(0, 10)
    print(r)
    if r < 5:
        msg = random.choice(spam_msgs)
        context.bot.send_message(job.context, text=msg)

def alarm(context):
    """Send the alarm message."""
    job = context.job
    context.bot.send_message(job.context, text='Beep!')

def calendar_notif(context):
    """ Check Calendar for dates and notify"""
    job = context.job
    cites_url = "http://miralosmorserver.pythonanywhere.com/api/calendar/all"
    cites_req = requests.get(cites_url)
    cites_dict = cites_req.json()
    cites_hour = [c['start'] for c in cites_dict]
    cite_stamps = [datetime.strptime(h, '%Y-%m-%dT%H:%M:%S.000Z') for h in cites_hour]
    cite_stamps_corrected = [(h - timedelta(hours=3)) for h in cite_stamps]
    for i in range(len(cite_stamps_corrected)):
        if datetime.today().date() == cite_stamps_corrected[i].date():
            msg = "Hoy tenemos " + cites_dict[i]['title'] + "a las " + cite_stamps_corrected[i].strftime("%H:%M hs")
            context.bot.send_message(job.context, text=msg)

def calendar_group(context):
    cites_url = "http://miralosmorserver.pythonanywhere.com/api/calendar/all"
    cites_req = requests.get(cites_url)
    cites_dict = cites_req.json()
    cites_hour = [c['start'] for c in cites_dict]
    cite_stamps = [datetime.strptime(h, '%Y-%m-%dT%H:%M:%S.000Z') for h in cites_hour]
    cite_stamps_corrected = [(h - timedelta(hours=3)) for h in cite_stamps]
    for i in range(len(cite_stamps_corrected)):
        if datetime.today().date() == cite_stamps_corrected[i].date():
            msg = "Hoy tenemos " + cites_dict[i]['title'] + "a las " + cite_stamps_corrected[i].strftime("%H:%M hs")
            context.bot.sendMessage(chat_id='@miralosmoriralertas', text=msg)
    

def set_timer(update, context):
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(context.args[0])
        if due < 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return

        # Add job to queue and stop current one if there is a timer already
        if 'job' in context.chat_data:
            old_job = context.chat_data['job']
            old_job.schedule_removal()
        new_job = context.job_queue.run_repeating(random_spam, interval=timedelta(minutes = 45), context=chat_id)
        context.chat_data['job'] = new_job

        update.message.reply_text('Timer successfully set!')
        msg = random.choice(spam_msgs)
        update.message.reply_text(text=msg)

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <seconds>')


def unset(update, context):
    """Remove the job if the user changed their mind."""
    if 'job' not in context.chat_data:
        update.message.reply_text('You have no active timer')
        return

    job = context.chat_data['job']
    job.schedule_removal()
    del context.chat_data['job']

    update.message.reply_text('Timer successfully unset!')


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler("set_spam", set_timer,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))

    h = "2020-09-22T12:00:00.000Z"

    daily_cal = datetime.strptime(h, '%Y-%m-%dT%H:%M:%S.000Z')


    

    # Start the Bot
    run(updater)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()