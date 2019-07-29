#!/usr/bin/env python3

from time import sleep
from threading import Thread

from flask import Flask, render_template
from flask_socketio import SocketIO, emit

from dublin_transport import DublinTransportData

UPDATE_INTERVAL = 60

dt = DublinTransportData()

app = Flask(__name__)
socketio = SocketIO(app)

def update_periodically():
    while True:
        update()
        sleep(UPDATE_INTERVAL)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def schedule_updates():
    update_thread = Thread(target=update_periodically)
    update_thread.start()

@socketio.on('get_update')
def update():
    data = dt.get_all_data()
    socketio.emit('update', data)
    return data

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
