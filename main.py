#!/usr/bin/env python
import win32evtlogutil
from win32evtlog import*
from win32event import*
from pywintypes import*
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None

def process_watcher():
	Sec_Handle		= OpenEventLog(None,"Security")
	Event_Handle	= CreateEvent(None,False,False,"Group_Add")
	Ch_Log = NotifyChangeEventLog(Sec_Handle,Event_Handle)
	Wait_for_Event = WaitForSingleObject(Event_Handle, INFINITE)
	if not Wait_for_Event:
		Event_Reader = ReadEventLog(Sec_Handle,EVENTLOG_BACKWARDS_READ | EVENTLOG_SEQUENTIAL_READ,0)
		if Event_Reader[0].EventID == 4732:
			TimeE = str(Event_Reader[0].TimeGenerated)
			return "\n[!](%s): Se ha movido de grupo un usuario en el sistema." %(TimeE)
		if Event_Reader[0].EventID == 4728:
			TimeE = str(Event_Reader[0].TimeGenerated)
			return "\n[!](%s): Se ha creado un usuario como administrador en el sistema." %(TimeE)
	CloseEventLog(Sec_Handle)


def background_thread():
    proceso = None
    while True:
        socketio.sleep(2)
        proceso = process_watcher()
        if proceso != None:
        	socketio.emit('my_response',{'data': proceso, 'count': 1},namespace='/test')

@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

@socketio.on('connect', namespace='/test')
def test_connect():
	emit('my_response', {'data': 'Connected', 'count': 0})
	global thread
	if thread is None:
		thread = socketio.start_background_task(target=background_thread)
    

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0')
