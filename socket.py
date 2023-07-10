# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 08:57:51 2023
@author: taeminHyeon
"""
import json
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
        list = params.split(',')  
        
        robotId = list[0] # 임시
        content = list[1] # 임시
        print("robot id ------>",list[0])
        print("content ------->",list[1])
        
        
# =============================================================================
#         now = datetime.datetime.now()
# 
#         time = str(now.year)+'-'+str(now.month)+'-'+str(now.day)+' '+str(now.hour)+':'+str(now.minute)+':'+str(now.second) #1000-00-00 00:00:00
#         with engine.connect() as connection:
#             connection.execute("INSERT INTO info (data, date) VALUES (%s, %s)", (params, time))
# =============================================================================

        #row = app.database.execute("""
        #        SELECT data
        #        FROM info 
        #        WHERE date = %s
        #    """, params).fetchone()

        # 연결된 클라이언트에 데이터 전송 (필요 없음)
        #socketio.emit('robotics_info', {'data': params}, namespace='/robotics_info')
        
        socketio.emit('client_info', {'data': content}, room=str(robotId), namespace='/robotics_info')
        
        
        return "Success"

    except Exception as e:
        return "An error occurred: {}".format(str(e))

@app.route("/api/sendRobotInfo", methods=['POST'])
def setInfo():
    try:
        params = request.get_data()  # 전달된 값을 저장
        params = str(params, "utf-8")
        
        if params == '':
            return "Params is null"
        
        #데이터를 어떤 형식으로 줄 지 정하지 않아 현재 ,를 기준으로 분리하여 리스트에 넣음 (임시)
        list = params.split(',')  
        
        robotId = list[0] # 임시
        content = list[1] # 임시
        
        
        print('robotid ----------------> '+str(list[0]))
        print('content ----------------> '+str(list[1]))
        #now = datetime.datetime.now()

        #time = str(now.year)+'-'+str(now.month)+'-'+str(now.day)+' '+str(now.hour)+':'+str(now.minute)+':'+str(now.second) #1000-00-00 00:00:00
        #with engine.connect() as connection:
        #    connection.execute("INSERT INTO info (data, date) VALUES (%s, %s)", (params, time))

        # Socket.IO를 사용하여 클라이언트에게 실시간으로 데이터 전달
        
        
        result = app.database.execute("""             
                                  SELECT USERID
                                  FROM connection 
                                  WHERE robotid = %s 
                                  """, robotId).fetchone()
        
        if result:
            userId = result[0]
        else:
            return 'Fail'
                                    
        print(userId) #userid만 뽑아와야함
        
        
        room_name = f"{robotId}{userId}"  # 방 이름 생성
        print(room_name)
        
        #robotics_info 이벤트 발생시킴 (html에 있음)
        socketio.emit('robotics_info', {'data': content}, room=room_name, namespace='/robotics_info')
        

        return "Success"

    except Exception as e:
        return "An error occurred : {}".format(str(e))
    
    

@app.route("/api/makeRoom",methods=["POST"])
def makeRoom():
    
    params = request.get_data()
    if params == '':
        return "Params is null"
    
    json_str = params.decode("utf-8") # 바이트 타입을 json
    params = json.loads(json_str) # json을 딕셔너리
    print(type(params)) 
    print(params)
    
    userid = params['userid'] # 유저 아이디 저장
    robotid = params['robotid'] # 로봇 아이디 저장 
    sid = params['sid']
    
    #userid = str(userid, "utf-8")# 전달된 로봇 id값을 저장
    #robotid = request.get_data("robotid")
    #robotid = str(robotid, "utf-8")
    

    
    print('user id ======>' +userid)
    print('robot id =====> '+robotid)
    
    
    # 로봇과 유저 아이디 db 존재 확인
    connection = app.database.execute("""             
                              SELECT ROBOTID, USERID
                              FROM connection 
                              WHERE robotid = %s AND userid = %s
                              """, robotid, userid).fetchone()
    
    print(connection)
                        
    if connection == '' : # 존재하지 않으면 fail
        return "Fail"                    
   
    
    if connection:
        room_name = f"{robotid}{userid}"  # 방 이름 생성
        print(room_name)
        
        socketio.emit('room_created', {'room_name': room_name},room=sid,namespace='/robotics_info')
        
        return "Success"
    else:
        return "Fail"

    
    


@app.route("/api/sendUserID", methods=['POST'])
def getID():
         
    try:
        params = request.get_data("")  # 전달된 로봇 id값을 저장
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
        
@socketio.on('join_room', namespace='/robotics_info') # 이벤트 join_room 발생시 호출 
def on_join_room(data):
    client_sid = request.sid
    print(f"Client request with SID: {client_sid}")
    room_name = data['room_name'] #data dic 에서 key 값이 room_name인 value를 가져옴
    
    join_room(room_name)  # 클라이언트를 방에 참여시킴
    print(f"Client joined room: {room_name}")
    print(f"Client success room with SID: {client_sid}")
    emit('room_joined', {'room_name': room_name}, namespace='/robotics_info')  # 클라이언트에게 'room_joined' 이벤트 전송
        
    
@socketio.on('connect', namespace='/robotics_info') # 클라이언트가 소켓 연결 시 호출
def on_connect():
    client_sid = request.sid
    print(f"Client connected with SID: {client_sid}")
    join_room(client_sid)
    user_agent = request.headers.get('User-Agent')
    print(f"Client User-Agent: {user_agent}")
    # 클라이언트의 세션 ID를 사용하여 방 이름 생성
   

    # 방 이름으로 클라이언트를 참여시킴
   


@socketio.on('disconnect', namespace='/robotics_info') # 클라이언트가 소켓 해제 시 호출
def on_disconnect():
    print('Client disconnected')
    client_sid = request.sid
    
    print(f"Client disconnected with SID: {client_sid}")

    
if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=2222,allow_unsafe_werkzeug=True)
    
