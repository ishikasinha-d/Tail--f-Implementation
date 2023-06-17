from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room
import os
import logging
import threading

app = Flask(__name__)
socket_io = SocketIO(app)
logging.basicConfig(filename="LogFile.log",
                    format='%(asctime)s %(message)s',
                    filemode='a')

filepath= "SampleLog.log"
num_of_lines= 10
prev_filesize= os.path.getsize(filepath)
connected_clients= set()

def tail():
    with open(filepath, 'r') as f:
        log_lines= f.readlines()
        logging.info(f"[INFO]: Sending last {num_of_lines} log lines to client ")
        return log_lines[-num_of_lines:]

def monitor_logs():
    global prev_filesize

    while True:
        curr_filesize= os.path.getsize(filepath)
        if(curr_filesize > prev_filesize):
            with open(filepath, 'r') as f:
                f.seek(prev_filesize)
                new_lines= f.readlines()
            prev_filesize= curr_filesize
            for client in connected_clients:
                socket_io.emit('log_update', {'data' : new_lines}, room= client)
        socket_io.sleep(1)

@socket_io.on('connect')
def client_connect():
    logging.info("[INFO]: Connected to Client ")
    connected_clients.add(request.sid)
    socket_io.emit('log_update', {'data': tail()}, room= request.sid)
    

@socket_io.on('disconnect')
def client_disconnect():
    logging.info("[INFO]: Disconnected from Client ")
    connected_clients.remove(request.sid)
    # leave_room("log_room")

@app.route('/log', methods= ["GET", "POST"])
def log_page():
    return render_template("index.html")
                        

@app.route('/')
def home_page():
    return "This is home page"
                        
if __name__ == '__main__':
    # for i in range(5):
    #     thread= threading.Thread(target = monitor_logs)
    #     thread.start()
    socket_io.start_background_task(monitor_logs)
    socket_io.run(app, host= "127.0.0.1", port= "5050", debug = True)