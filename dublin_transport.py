#!/usr/bin/env python3

from urllib.request import urlopen
from os.path import join, expanduser
from json import loads, dumps
from configparser import ConfigParser

class RTPIError(Exception): pass

class DublinTransportData:

    RTPI_URL =  ('https://data.smartdublin.ie/cgi-bin/rtpi/'
                'realtimebusinformation?stopid={}')
    
    DB_URL =    ('https://api.jcdecaux.com/vls/v1/stations/{}'
                '?contract=Dublin&apiKey={}')

    WU_URL =    ('http://api.wunderground.com/api/{}/'
                'conditions/q/ie/{}.json')

    def __init__(self, conf_file=None):
        
        self.conf_file = conf_file or expanduser('~/.config/dublin_transport.ini')
        self.load_config()

    def load_config(self):

        self.config = ConfigParser()
        self.config.optionxform = lambda option: option
        self.config.read(self.conf_file)

        self.RESULT_COUNT = self.config.getint('CONFIG_VALUES', 'RESULT_COUNT')
        self.DB_API_KEY = self.config['CONFIG_VALUES']['DB_API_KEY']
        self.WU_API_KEY = self.config['CONFIG_VALUES']['WU_API_KEY']

        self.LUAS_STOPS = self.config['LUAS_STOPS']
        self.BUS_STOPS = self.config['BUS_STOPS']
        self.BIKE_STOPS = self.config['BIKE_STOPS']
        self.WEATHER_STATIONS = self.config['WEATHER_STATIONS']

    def get_all_data(self):

        results = {'LUAS': {}, 'BUS': {}, 'BIKE': {}, 'WEATHER': {}}

        for stop in self.LUAS_STOPS:
            stop_id = self.LUAS_STOPS[stop]
            results['LUAS'][stop] = self.fetch_rtpi_data(stop_id)
        for stop in self.BUS_STOPS:
            stop_id = self.BUS_STOPS[stop]
            results['BUS'][stop] = self.fetch_rtpi_data(stop_id)
        for stop in self.BIKE_STOPS:
            stop_id = self.BIKE_STOPS[stop]
            results['BIKE'] = self.fetch_bike_data(stop_id)
        for station in self.WEATHER_STATIONS:
            station_id = self.WEATHER_STATIONS[station]
            results['WEATHER'][station] = self.fetch_weather_data(station_id)
        return results

    # Functions to fetch data from APIs

    def fetch_weather_data(self, station_id):

        url = self.WU_URL.format(self.WU_API_KEY, station_id)
        json_data = urlopen(url).read().decode()
        data = loads(json_data)['current_observation']
        weather = data['weather']
        temp = '{}ºC (feels like {}ºC)'.format(data['temp_c'],
                    data['feelslike_c'])
        wind = '{} ({} kmph {})'.format(data['wind_string'],
                    data['wind_kph'], data['wind_dir'])
        humidity = 'Humidity: {}'.format(data['relative_humidity'])
        return weather, temp, wind, humidity

    def fetch_rtpi_data(self, stop_id):

        url = self.RTPI_URL.format(stop_id)
        json_data = urlopen(url).read().decode()
        data = loads(json_data)
        if data['errorcode'] == '0':
            results = data['results'][:self.RESULT_COUNT]
            return [(r['route'], r['destination'], r['duetime']) for r in results]
        elif data['errorcode'] == '1':
            return None
        else:
            raise RTPIError(data['errorcode'], data['errormessage'])

    def fetch_bike_data(self, stop_id):

        url = self.DB_URL.format(stop_id, self.DB_API_KEY)
        json_data = urlopen(url).read().decode()
        data = loads(json_data)
        return data['status'], data['available_bikes'], data['bike_stands']

# Callable for WSGI so that script can run as webserver

def application(environ, start_response):
    dtd = DublinTransportData()
    data = dtd.get_all_data()
    start_response('200 OK', [('Content-Type','application/json'),
        ('Access-Control-Allow-Origin', '*')])
    return [bytes(dumps(data), 'utf-8')]

if __name__ == '__main__':
    dtd = DublinTransportData()
    print(dtd.get_all_data())
