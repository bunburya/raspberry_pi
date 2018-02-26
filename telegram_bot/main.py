#!/usr/bin/env python3

import time
import telepot

from os import mkdir
from os.path import join, expanduser, dirname

from plugin_handler import Plugin, PluginHandler


class Bot:

    def __init__(self):

        self.confdir = join(expanduser('~'), '.telegram_bot')
        self.plugindir = join(dirname(__file__), 'plugins')

        try:
            with open(join(self.confdir, 'bot_token')) as f:
                self.bot_token = f.read().strip()
            with open(join(self.confdir,'chat_id')) as f:
                self.valid_id = int(f.read())
        except FileNotFoundError:
            print('Token and / or valid ID file not found.')
            return
                    
        self.plugin_handler = PluginHandler(self, self.plugindir)
        self.plugin_handler.load_all_plugins()

        self.run()        
    
    def handle_globally(self, content_type, msg):
        if content_type == 'text':
            print('Text is: {}'.format(msg['text']))
        elif content_type in {'photo', 'audio'}:
            caption = msg.get('caption')
            if caption is None:
                print('No caption.')
            else:
                print('Caption is {}'.format(caption))
        else:
            self.handle_other(msg)
    
    def handle_other(self, msg):
        pass
    
    def handle(self, msg):
    
        content_type, msg_type, chat_id, msg_date, msg_id = telepot.glance(msg, long=True)
        print('Got message of type {} from ID {}'.format(content_type, chat_id))
        
        if chat_id != self.valid_id:
            print('ID {} not valid.'.format(chat_id))
            self.bot.sendMessage(self.valid_id,
                'Unauthorised message {} from ID {}.'.format(chat_id, chat_id))
            return
        else:
            self.handle_globally(content_type, msg)
            self.plugin_handler.call_handlers(content_type, msg)

    def run(self):
        self.bot = telepot.Bot(self.bot_token)
        self.bot.message_loop(self.handle)

        print('Listening.')

        while 1:
            time.sleep(5)

if __name__ == '__main__':
    b = Bot()
