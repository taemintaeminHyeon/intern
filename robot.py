import socketio

def handle_response(data):
    message = data['data']
    print(robotID, ' Received message:', message)


sio = socketio.Client()
sio.connect("http://192.168.0.152:2222",namespaces=['/robotics_info'])
ssid=sio.sid
print(ssid)

robotID = "robot1"
room_name = robotID  # 서버와 파이썬 코드가 동일한 방에 속해야 함

sio.emit('join_room', {'room_name': room_name}, namespace='/robotics_info')

# 그러면 자신의 robotid를 서버로 전달하고 해당 sid를 찾아 그 room에만 join_room으로 가는 서버 코드를 추가해야할듯

@sio.on('client_info',namespace='/robotics_info')
def on_client_info(data):
    handle_response(data)
    

try:
    while True:
        sio.sleep(0.1)
except KeyboardInterrupt:
    sio.disconnect()









