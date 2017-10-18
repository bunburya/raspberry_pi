from os import listdir
from os.path import basename

from importlib import import_module
from subprocess import check_output

class PluginRegister(type):
    
    def __init__(cls, name, base, attrs):
        
        if not hasattr(cls, 'plugins'):
            print('initialising plugins')
            cls.plugins = []
        else:
            cls.plugins.append(cls())
            print(cls.plugins)


class Plugin(object, metaclass=PluginRegister):
        
    def _call(self, args):
        """Call system command."""
        fn = args[0]
        try:
            output = check_output(args)
        except Exception:
            output = 'Encountered error when calling {}.'.format(fn)
        return output
    
    def _send_call_output(self, msg, args):
        chat_id = msg['chat']['id']
        output = self._call(args)
        self.bot.bot.sendMessage(chat_id, output)
    
    def handle_other(self, msg): pass

class PluginHandler:
    
    def __init__(self, bot, plugindir):
        self.bot = bot
        Plugin.bot = bot
        self.plugindir = plugindir
    
    def load_all_plugins(self):
        plugin_files = filter(
            lambda fname: fname.endswith('.py') and not fname == '__init__.py',
            listdir(self.plugindir))
        for f in plugin_files:
            self.load_plugin(f[:-3])
    
    def load_plugin(self, p):
        fname = '.'.join((basename(self.plugindir), p))
        import_module(fname)
        print('Loaded plugin {}.'.format(p))

    def call_handlers(self, content_type, msg):
        for p in Plugin.plugins:
            p.handlers.get(content_type, p.handle_other)(msg)
                
