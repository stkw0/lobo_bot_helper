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
        self._ignore_list = []

        # Users that talked in the last self.range minutes will be notified
        self.range = 20

    def update_user_activity(self, update):
        user = update.message.from_user.name
        now = update.message.date
        self.last_user_activity[user] = now

    def get_active_users_str(self, update):
        user = update.message.from_user.name
        now = update.message.date
        mention_list = ""
        for k in self.last_user_activity.keys():
            if k and k != user and user not in self._ignore_list:
                diff = new - self.last_user_activity[k]
                if diff.total_seconds() / 60 < self.range:
                    mention_list += k + " "

        return mention_list

    def set_range(self, num):
        # TODO: Report error if <= 0
        if num > 0:
            self.range = num

    def clear(self):
        self.last_user_activity = {}

    def ignore_user(self, update):
        self._ignore_list.append(update.message.from_user.name)

    def clear_ignore_list(self, update):
        self._ignore_list = []

class Luperca:

    def __init__(self):
        self.updater = Updater(token=getenv("BOT_API"))
        dispatcher = self.updater.dispatcher

        notify_handler = CommandHandler('notify_players', self.notify_users)
        dispatcher.add_handler(notify_handler)

        clear_handler = CommandHandler('clear', self.clear)
        dispatcher.add_handler(clear_handler)

        clear_ignores = CommandHandler('clear_ignore_list', self.clear_ignore_list)
        dispatcher.add_handler(clear_ignores)

        help_handler = CommandHandler('help', self.help)
        dispatcher.add_handler(help_handler)

        range_handler = CommandHandler('set_range', self.set_range, pass_args=True)
        dispatcher.add_handler(range_handler)

        ignore_handler = CommandHandler('ignore_me', self.ignore_user)
        dispatcher.add_handler(ignore_handler)

        unknown_handler = MessageHandler(Filters.command, self.unknown)
        dispatcher.add_handler(unknown_handler)

        update_handler = MessageHandler(Filters.text, self.update_user_activity)
        dispatcher.add_handler(update_handler)

        self.groups = {}

    def help(self, bot, update):
        message =   """
/notify_players: Notify who talked in the last X minutes (X=20 by default)
/set_range: Change those X minutes (it have to be > 0)
/clear: Clears the users activity
/ignore_me: Add you to list of users that don't want to be notified
/clear_ignore_list: Remove all users from the ignore list
/help: this

Note: For now information is stored on memory, so all settings will be lost eventually

Bugs, ideas an such: https://github.com/stkw0/lobo_bot_helper
"""
        bot.send_message(chat_id=update.message.chat_id, text=message)

    def clear_ignore_list(self, bot, update):
        chat_id = update.message.chat_id

        if chat_id in self.groups:
            self.groups[chat_id].clear_ignore_list()

        bot.send_message(chat_id=chat_id, text="OK")

    def ignore_user(self, bot, update):
        chat_id = update.message.chat_id

        if not chat_id in self.groups:
            self.groups[chat_id] = Group()

        if chat_id in self.groups:
            self.groups[chat_id].ignore_user(update)

        bot.send_message(chat_id=chat_id, text="OK")

    def clear(self, bot, update):
        chat_id = update.message.chat_id

        if chat_id in self.groups:
            self.groups[chat_id].clear()

        bot.send_message(chat_id=chat_id, text="OK")

    def set_range(self, bot, update, args):
        chat_id = update.message.chat_id

        if len(args) != 1:
            bot.send_message(chat_id=chat_id, text="Invalid number of arguments")
            return

        if not chat_id in self.groups:
            self.groups[chat_id] = Group()

        if chat_id in self.groups:
            self.groups[chat_id].set_range(int(args[0]))

        bot.send_message(chat_id=chat_id, text="OK")

    def update_user_activity(self, bot, update):
        chat_id = update.message.chat_id

        if not chat_id in self.groups:
            self.groups[chat_id] = Group()

        self.groups[chat_id].update_user_activity(update)

    def notify_users(self, bot, update):
        chat_id = update.message.chat_id

        if chat_id in self.groups:
            n_list = self.groups[chat_id].get_active_users_str(update)

            # XXX: Ugly
            if n_list == "":
                n_list="No users to notify"

            bot.send_message(chat_id=chat_id, text=n_list)
        else:
            bot.send_message(chat_id=chat_id, text="No users to notify")

    def unknown(self, bot, update):
        bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")

    def start_bot(self):
        self.updater.start_polling(clean=True)
        self.updater.idle()


def main():
    l = Luperca()
    l.start_bot();

if __name__ == '__main__':
    main()

