# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 08:57:51 2023
@author: jbr
"""

from flask import Flask, request, render_template
import datetime
from sqlalchemy import create_engine
from flask_socketio import SocketIO, emit

engine = create_engine("mysql+mysqlconnector://root:1234@localhost/testdb")
app = Flask(__name__)
app.config.from_pyfile("config.py")
database = create_engine(app.config['DB_URL'], encoding='utf-8', max_overflow=0)
app.database = database
socketio = SocketIO(app)  # SocketIO 초기화


@app.route("/")
def index():
    return render_template('test.html')

@app.route("/api/getRoboticsInfo", methods=['POST', 'GET'])
def getInfo():
    try:
        params = request.get_data()  # 전달된 값을 저장
        params = str(params, "utf-8")
        if params == '':
            return "Params is null"

        print(params)
        
        now = datetime.datetime.now()

        time = str(now.year)+'-'+str(now.month)+'-'+str(now.day)+' '+str(now.hour)+':'+str(now.minute)+':'+str(now.second) #1000-00-00 00:00:00
        with engine.connect() as connection:
            connection.execute("INSERT INTO info (data, date) VALUES (%s, %s)", (params, time))

        #row = app.database.execute("""
        #        SELECT data
        #        FROM info 
        #        WHERE date = %s
        #    """, params).fetchone()

        # 연결된 클라이언트에 데이터 전송
        socketio.emit('robotics_info', {'data': params}, namespace='/robotics_info')

        return "Success"

    except Exception as e:
        return "An error occurred: {}".format(str(e))

@app.route("/api/setRoboticsInfo", methods=['POST'])
def setInfo():
    try:
        params = request.get_data()  # 전달된 json값을 저장
        params = str(params, "utf-8")
        if params == '':
            return "Params is null"
        now = datetime.datetime.now()

        #time = str(now.year)+'-'+str(now.month)+'-'+str(now.day)+' '+str(now.hour)+':'+str(now.minute)+':'+str(now.second) #1000-00-00 00:00:00
        #with engine.connect() as connection:
        #    connection.execute("INSERT INTO info (data, date) VALUES (%s, %s)", (params, time))

        # Socket.IO를 사용하여 클라이언트에게 실시간으로 데이터 전달
        socketio.emit('robotics_info', {'data': params}, namespace='/robotics_info') # namespace로 구

        return "Success"

    except Exception as e:
        return "An error occurred : {}".format(str(e))

@socketio.on('connect', namespace='/robotics_info')
def on_connect():
    print('Client connected')

@socketio.on('disconnect', namespace='/robotics_info')
def on_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=2222,allow_unsafe_werkzeug=True)
    
