#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import logging
from os import getenv

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class Group:

    def __init__(self):
        self.last_user_activity = {}

    def update_user_activity(self, update):
        print(update)
        print("")
        user = update.message.from_user.name
        now = update.message.date
        self.last_user_activity[user] = now

    def get_active_users_str(self, update):
        user = update.message.from_user.name
        now = update.message.date
        mention_list = ""
        mention_list += user + " "
        for k in self.last_user_activity.keys():
            if k and k != user:
                diff = new - self.last_user_activity[k]
                if diff.total_seconds() / 60 < 20:
                    mention_list += k + " "

        return mention_list


class Luperca:

    def __init__(self):
        self.updater = Updater(token=getenv("BOT_API"))
        dispatcher = self.updater.dispatcher

        start_handler = CommandHandler('notify_players', self.notify_users)
        dispatcher.add_handler(start_handler)

        unknown_handler = MessageHandler(Filters.command, self.unknown)
        dispatcher.add_handler(unknown_handler)

        echo_handler = MessageHandler(Filters.text, self.echo)
        dispatcher.add_handler(echo_handler)

        self.groups = {}

    def echo(self, bot, update):
        chat_id = update.message.chat_id

        if not chat_id in self.groups:
            self.groups[chat_id] = Group()

        self.groups[chat_id].update_user_activity(update)
        #bot.send_message(chat_id=chat_id, text=update.message.text)

    def notify_users(self, bot, update):
        chat_id = update.message.chat_id

        if chat_id in self.groups:
            n_list = self.groups[chat_id].get_active_users_str(update)
            bot.send_message(chat_id=chat_id, text=n_list)
        else:
            bot.send_message(chat_id=chat_id, text="No users to notify")

    def unknown(self, bot, update):
        print(update)
        bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")

    def start_bot(self):
        self.updater.start_polling(clean=True)
        self.updater.idle()


def main():
    l = Luperca()
    l.start_bot();

if __name__ == '__main__':
    main()

