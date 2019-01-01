from json import dumps
from dublin_transport import DublinTransportData

def application(environ, start_response):
    dtd = DublinTransportData()
    data = dtd.get_all_data()
    start_response('200 OK', [('Content-Type', 'application/json'),
        ('Access-Control-Allow-Origin', '*')])
    return [bytes(dumps(data), 'utf-8')]
