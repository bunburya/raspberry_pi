from plugin_handler import Plugin

from dublin_transport import DublinTransportData

class TransportPlugin(Plugin):
    
    def __init__(self):
        self.handlers = {'text': self.handle_text}
        self.dtd = DublinTransportData()
            
    def handle_text(self, msg):
        chat_id = msg['chat']['id']
        text = msg['text'].lower()
        if text == 'transport':
            self.send_transport_data(chat_id)

    def send_transport_data(self, chat_id):
        self.send_luas_data(chat_id)
        self.send_bus_data(chat_id)

    def send_bus_data(self, chat_id):
        self.bot.bot.sendMessage(chat_id, 'BUS:')
        try:
            data = self.dtd.get_rtpi_data('BUS')
        except Exception as e:
            self.bot.bot.sendMessage(chat_id, 'Error fetching data.')
            raise e
        for bus in data['Inbound']:
            route, dest, stop, due = bus['route'], bus['destination'], bus['stop'], bus['duetime']
            if due == 'Due':
                due_str = 'now'
            else:
                due_str = 'in {} minutes'.format(due)
            self.bot.bot.sendMessage(chat_id, '{} to {} (from {}), due {}.'.format(route, dest, stop, due_str))
        if not data['Inbound']:
            self.bot.bot.sendMessage(chat_id, 'No buses due.')

    def send_luas_data(self, chat_id):
        self.bot.bot.sendMessage(chat_id, 'LUAS:')
        try:
            data = self.dtd.get_rtpi_data('LUAS')
        except Exception as e:
            self.bot.bot.sendMessage(chat_id, 'Error fetching data.')
            raise e
        for luas in data['Inbound']:
            stop, dest, due = luas['stop'], luas['destination'].lstrip('LUAS '), luas['duetime']
            self.bot.bot.sendMessage(chat_id, '{} to {}, due in {} minutes.'.format(stop, dest, due))
        if not data['Inbound']:
            self.bot.bot.sendMessage(chat_id, 'No Luas due.')
