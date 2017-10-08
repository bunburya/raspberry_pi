#!/usr/bin/env python3

import time
import telepot

from subprocess import check_output
from os import remove, mkdir
from os.path import join, expanduser

import raspicam_utils

class Bot:

    def __init__(self):

        self.confdir = join(expanduser('~'), '.telegram_bot')

        try:
            with open(join(self.confdir, 'bot_token')) as f:
                self.bot_token = f.read().strip()
            with open(join(self.confdir,'chat_id')) as f:
                self.valid_id = int(f.read())
        except FileNotFoundError:
            print('Token and / or valid ID file not found.')
            return
            
        self.raspicam = raspicam_utils.RaspiCam()
        
        self.commands = {
            'uname': lambda chat_id: self.call(['uname', '-a']),
            'uptime': lambda chat_id: self.call(['uptime']),
            'photo': self.send_photo,
            'record': self.send_audio
            }

        self.run()

    def call(self, args):
        """Call system command."""
        fn = args[0]
        try:
            output = check_output(args)
        except Exception:
            output = 'Encountered error when calling {}.'.format(fn)
        return output

    def send_photo(self, chat_id):
        self.bot.sendMessage(chat_id, 'Taking photo...')
        tmp_fpath = join('/tmp', 'raspicam_'+str(time.time())+'.jpg')
        self.raspicam.take_photo(tmp_fpath)
        with open(tmp_fpath, 'rb') as f:
            self.bot.sendPhoto(chat_id, f)
        remove(tmp_fpath)

    def send_audio(self, chat_id, t=5):
        self.bot.sendMessage(chat_id, 'Recording audio for {} seconds...'.format(t))
        tmp_fpath = join('/tmp', 'record_'+str(time.time())+'.wav')
        self.call(['arecord', tmp_fpath, '--format=S16_LE',
            '--channels=2', '--device=sysdefault:CARD=1',
            '--duration={}'.format(t)])
        with open(tmp_fpath, 'rb') as f:
            self.bot.sendAudio(chat_id, f)
        remove(tmp_fpath)

    def handle(self, msg):
    
        txt = msg['text']
        chat_id = msg['chat']['id']
        print('Got text {} from ID {}'.format(txt, chat_id))

        if chat_id != self.valid_id:
            print('ID {} not valid.'.format(chat_id))
            self.bot.sendMessage(self.valid_id,
                'Unauthorised message {} from ID {}.'.format(chat_id, txt))
            return
        
        tokens = txt.split()
        cmd = tokens[0].lower()

        output_callable = self.commands.get(cmd)
        if output_callable:
            response = output_callable(chat_id, *tokens[1:])
            if response:
                self.bot.sendMessage(chat_id, response)

    def run(self):
        self.bot = telepot.Bot(self.bot_token)
        self.bot.message_loop(self.handle)

        print('Listening.')

        while 1:
            time.sleep(5)

if __name__ == '__main__':
    b = Bot()
