from plugin_handler import Plugin

class SysInfoPlugin(Plugin):
    
    def __init__(self):
        self.handlers = {'text': self.handle_text}
            
    def handle_text(self, msg):
        text = msg['text'].lower()
        if text == 'uname':
            self._send_call_output(msg, ['uname', '-a'])
        elif text == 'uptime':
            self._send_call_output(msg, ['uptime'])
