#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import logging
import telegram
from datetime import datetime
from telegram.error import NetworkError, Unauthorized
from time import sleep
from os import getenv


update_id = None

def main():
    global update_id
    # Telegram Bot Authorization Token
    bot = telegram.Bot(getenv("BOT_API"))

    # get the first pending update_id, this is so we can skip over it in case
    # we get an "Unauthorized" exception.
    try:
        update_id = bot.get_updates()[0].update_id
    except IndexError:
        update_id = None

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    users_map = {}

    while True:
        try:
            prev_date = datetime.now()
            # Request updates after the last update_id
            for update in bot.get_updates(offset=update_id, timeout=10):
                update_id = update.update_id + 1


                if update.message:  # your bot can receive updates without messages
                    if update.message.text == "!get lobo" or update.message.text == "!lets_play":
                        continue
                        user = update.message.from_user.username
                        new = update.message.date
                        mention_list = ""
                        mention_list += "@"+user + " "
                        for k in users_map.keys():
                            if k and k != user:
                                diff = new - users_map[k]
                                if diff.total_seconds() / 60 < 20:
                                    mention_list += "@"+k + " "
                        #update.message.reply_text(mention_list)
                    else:
                        print(update.message.text)
                        user = update.message.from_user.username
                        new = update.message.date
                        users_map[user] = new
                        # Reply to the message
                        #
        except NetworkError:
            sleep(1)
        except Unauthorized:
            # The user has removed or blocked the bot.
            update_id += 1

if __name__ == '__main__':
    main()

