import time

from os import remove
from os.path import join

from plugin_handler import Plugin

import raspicam_utils

class MonitorPlugin(Plugin):
    
    
    
    def __init__(self):
        self.raspicam = raspicam_utils.RaspiCam()
        self.handlers = {'text': self.handle_text}
    
    def send_photo(self, chat_id):
        self.bot.bot.sendMessage(chat_id, 'Taking photo...')
        tmp_fpath = join('/tmp', 'raspicam_'+str(time.time())+'.jpg')
        self.raspicam.take_photo(tmp_fpath)
        with open(tmp_fpath, 'rb') as f:
            self.bot.bot.sendPhoto(chat_id, f)
        remove(tmp_fpath)

    def send_audio(self, chat_id, t=5):
        self.bot.bot.sendMessage(chat_id, 'Recording audio for {} seconds...'.format(t))
        tmp_fpath = join('/tmp', 'record_'+str(time.time())+'.wav')
        self._call(['arecord', tmp_fpath, '--format=S16_LE',
            '--channels=2', '--device=sysdefault:CARD=1',
            '--duration={}'.format(t)])
        with open(tmp_fpath, 'rb') as f:
            self.bot.bot.sendAudio(chat_id, f)
        remove(tmp_fpath)
    
    def handle_text(self, msg):
        chat_id = msg['chat']['id']
        text = msg['text'].lower()
        tokens = text.split()
        cmd = tokens[0]
        
        if cmd == 'photo':
            self.send_photo(chat_id)
        elif cmd == 'record':
            self.send_audio(chat_id, *tokens[1:])
