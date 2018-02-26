#!/usr/bin/env python3

from urllib.request import urlopen
from json import loads, dumps

class RTPIError(Exception): pass

class DublinTransportData:

    # URLs

    RTPI_URL =  ('https://data.smartdublin.ie/cgi-bin/rtpi/'
                'realtimebusinformation?stopid={}')
    
    BIKE_URL =  ('https://api.jcdecaux.com/vls/v1/stations/{}'
                '?contract=Dublin&apiKey={}')

    # Functions to fetch data

    def get_rtpi_data(self, stop_id):

        url = self.RTPI_URL.format(stop_id)
        json_data = urlopen(url).read().decode()
        data = loads(json_data)
        if data['errorcode'] != '0':
            raise RTPIError(data['errorcode'], data['errormessage'])
        results = data['results'][:self.RESULT_COUNT]
        for r in results:
            return r['route'], r['destination'], r['duetime']

    def get_bike_data(self, stop_id):

        url = self.BIKE_URL.format(stop_id, self.BIKE_API_KEY)
        json_data = urlopen(url).read().decode()
        data = loads(json_data)
        return data['status'], data['available_bikes'], data['bike_stands']

if __name__ == '__main__':
    dtd = DublinTransportData()
    for s in dtd.LUAS_STOPS:
        print(dtd.get_rtpi_data(dtd.LUAS_STOPS[s]))
    for s in dtd.BUS_STOPS:
        print(dtd.get_rtpi_data(dtd.BUS_STOPS[s]))
    for s in dtd.BIKE_STOPS:
        print(dtd.get_bike_data(dtd.BIKE_STOPS[s]))
