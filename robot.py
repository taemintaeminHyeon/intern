import socketio

def handle_response(data):
    message = data['data']
    print('Received message:', message)


sio = socketio.Client()
sio.connect("http://192.168.0.152:2222",namespaces=['/robotics_info'])
ssid=sio.sid
print(ssid)

robotID = "robot1"
room_name = robotID  # 서버와 파이썬 코드가 동일한 방에 속해야 함

sio.emit('join_room', {'room_name': room_name}, namespace='/robotics_info')

@sio.on('client_info',namespace='/robotics_info')
def on_client_info(data):
    handle_response(data)

while True:
    sio.sleep(0.1)









