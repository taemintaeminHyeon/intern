# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 08:57:51 2023
@author: taeminHyeon
"""

from flask import Flask, request, render_template
import datetime
from sqlalchemy import create_engine
from flask_socketio import SocketIO, emit, join_room

engine = create_engine("mysql+mysqlconnector://root:1234@localhost/testdb")
app = Flask(__name__)
app.config.from_pyfile("config.py")
database = create_engine(app.config['DB_URL'], encoding='utf-8', max_overflow=0)
app.database = database
socketio = SocketIO(app, manage_session=False)  # SocketIO 초기화


rooms= {}  #다수의 방 생성

@app.route("/")
def index():
    return render_template('test.html')

@app.route("/api/getRoboticsInfo", methods=['POST', 'GET']) # 로봇에게 줄 정보 db에 저장
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

        # 연결된 클라이언트에 데이터 전송 (필요 없음)
        #socketio.emit('robotics_info', {'data': params}, namespace='/robotics_info')

        return "Success"

    except Exception as e:
        return "An error occurred: {}".format(str(e))

@app.route("/api/sendRobotInfo", methods=['POST'])
def setInfo():
    try:
        params = request.get_data()  # 전달된 값을 저장
        params = str(params, "utf-8")
        robotid = "robot1"
        userid="user1"
        if params == '':
            return "Params is null"
        #now = datetime.datetime.now()

        #time = str(now.year)+'-'+str(now.month)+'-'+str(now.day)+' '+str(now.hour)+':'+str(now.minute)+':'+str(now.second) #1000-00-00 00:00:00
        #with engine.connect() as connection:
        #    connection.execute("INSERT INTO info (data, date) VALUES (%s, %s)", (params, time))

        # Socket.IO를 사용하여 클라이언트에게 실시간으로 데이터 전달
        room_name = f"{robotid}{userid}"  # 방 이름 생성
        print(room_name)
        socketio.emit('robotics_info', {'data': params}, room=room_name, namespace='/robotics_info')

        return "Success"

    except Exception as e:
        return "An error occurred : {}".format(str(e))
    
    

@app.route("/api/makeRoom",methods=["POST"])
def makeRoom():
    robotid = "robot1"
    userid="user1"
    
    connection = app.database.execute("""             
                              SELECT ROBOTID, USERID
                              FROM connection 
                              WHERE robotid = %s and userid = %s
                              """, robotid, userid).fetchone()
    
    if connection:
        room_name = f"{robotid}{userid}"  # 방 이름 생성
        print(room_name)
        socketio.emit('join_room', {'room_name': room_name}, namespace='/robotics_info')
        socketio.emit('room_created', {'room_name': room_name}, namespace='/robotics_info')
        return "Success"
    else:
        return "Fail"

    
    


@app.route("/api/sendRobotID", methods=['POST'])
def getID():
    # db에 유저 id 있으면 좋을 듯     
    try:
        params = request.get_data()  # 전달된 로봇 id값을 저장
        params = str(params, "utf-8")
        if params == '':
            return "Params is null"

        #로봇 id 조회
        ID = app.database.execute("""             
                                  SELECT ROBOTID
                                  FROM connection 
                                  WHERE date = %s
                                  """, params).fetchone()
        
        #로봇 id 없는 경우 추가
        if ID == "":
            with engine.connect() as connection:
                connection.execute("INSERT INTO robotid (ROBOTID) VALUES (%s)", (params))
        
        
        
        return "Success"
    
    except Exception as e:
        return "An error occurred: {}".format(str(e))
        
@socketio.on('join_room', namespace='/robotics_info')
def on_join_room(data):
    room_name = data['room_name']
    join_room(room_name)  # 클라이언트를 방에 참여시킴
    print(f"Client joined room: {room_name}")
    emit('room_joined', {'room_name': room_name}, namespace='/robotics_info')  # 클라이언트에게 'room_joined' 이벤트 전송

    
@socketio.on('connect', namespace='/robotics_info')
def on_connect():
    client_sid = request.sid
    print(f"Client connected with SID: {client_sid}")
    user_agent = request.headers.get('User-Agent')
    print(f"Client User-Agent: {user_agent}")


@socketio.on('disconnect', namespace='/robotics_info')
def on_disconnect():
    print('Client disconnected')
    client_sid = request.sid
    print(f"Client disconnected with SID: {client_sid}")

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=2222,allow_unsafe_werkzeug=True)
    
