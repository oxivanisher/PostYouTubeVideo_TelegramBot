#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to send timed Telegram messages.

This Bot uses the Updater class to handle the bot and the JobQueue to send
timed messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Alarm Bot example, sends a message after a set time.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import yaml
#import dill

with open(r'config.yaml') as file:
    config = yaml.full_load(file)

from telegram.ext import Updater, CommandHandler, PicklePersistence

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def time_until_next_run(every):

    return 10


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    new_job = context.job_queue.run_once(show_timed_video, time_until_next_run(config['every']), context=context)
    context.chat_data['job'] = new_job

    update.message.reply_text('My dudes, I will send you the videos')


def show_timed_video(context):
    """Send the next video link."""
    job = context.job

    last_video = 0
    if 'last_video' in context.chat_data:
        last_video = context.chat_data['last_video']

    next_video = last_video + 1
    context.chat_data['last_video'] = next_video

    new_job = context.job_queue.run_once(show_timed_video, time_until_next_run(config['every']), context=context)
    context.chat_data['job'] = new_job

    context.bot.send_message(job.context,
                             text='It Is Wednesday My Dudes!\nhttps://www.youtube.com/watch?v=%s'
                                  % config['video_ids'][next_video])


# def set_timer(update, context):
#     """Add a job to the queue."""
#     chat_id = update.message.chat_id
#     try:
#         # args[0] should contain the time for the timer in seconds
#         due = int(context.args[0])
#         if due < 0:
#             update.message.reply_text('Sorry we can not go back to future!')
#             return
#
#         # Add job to queue and stop current one if there is a timer already
#         if 'job' in context.chat_data:
#             old_job = context.chat_data['job']
#             old_job.schedule_removal()
#         new_job = context.job_queue.run_once(alarm, due, context=chat_id)
#         context.chat_data['job'] = new_job
#
#         update.message.reply_text('Timer successfully set!')
#
#     except (IndexError, ValueError):
#         update.message.reply_text('Usage: /set <seconds>')


def status(update, context):
    """Show how many videos already have been showed"""

    last_video = 0
    if 'last_video' in context.chat_data:
        last_video = context.chat_data['last_video']

    videos_total = len(config['video_ids'])
    update.message.reply_text('I showed this channel %s of %s videos' % (last_video, videos_total))


def show_video(update, context):
    """Show a video"""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the video id
        video_id = int(context.args[0])
        if video_id < 1 or video_id > len(config['video_ids']):
            update.message.reply_text('This is not possible!')
            return

        update.message.reply_text('https://www.youtube.com/watch?v=%s' % config['video_ids'][video_id])

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /show video_id # which can be 1 to %s' % len(config['video_ids']))



# def unset(update, context):
#     """Remove the job if the user changed their mind."""
#     if 'job' not in context.chat_data:
#         update.message.reply_text('You have no active timer')
#         return
#
#     job = context.chat_data['job']
#     job.schedule_removal()
#     del context.chat_data['job']
#
#     update.message.reply_text('Timer successfully unset!')


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Run bot."""
    # make the bot persistent
    persistence = PicklePersistence(filename='bot_persistence', store_user_data=False, store_bot_data=False, store_chat_data=False)
    # persistence = DictPersistence()

    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(config['telegram_token'], use_context=True, persistence=persistence)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    # dp.add_handler(CommandHandler("set", set_timer,
    #                               pass_args=True,
    #                               pass_job_queue=True,
    #                               pass_chat_data=True))
    dp.add_handler(CommandHandler("status", status,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("show", show_video,
                                  pass_args=True,
                                  pass_chat_data=True))
    # dp.add_handler(CommandHandler("unset", unset, pass_chat_data=True))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
