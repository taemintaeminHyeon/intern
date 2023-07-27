import requests
import time

def send_post_request(url, data):
    try:
        
        
        response = requests.post(url, data=data)
        # 만약 JSON 데이터를 보내고 싶다면 아래 코드를 사용합니다.
        # response = requests.post(url, json=data)
        
        response_time = response.elapsed.total_seconds()
        print("응답 시간:", response_time, "초")

        # 서버로부터 성공적인 응답을 받았는지 확인합니다.
        if response.status_code == 200:
            print("요청이 성공적으로 보내졌습니다.")
            print("서버 응답:", response.text)
        else:
            print("요청이 실패했습니다.")
            print("에러 코드:", response.status_code)
            print("에러 메시지:", response.text)

    except requests.exceptions.RequestException as e:
        print("요청 중 오류가 발생했습니다:", e)

if __name__ == "__main__":
    # 요청을 보낼 서버의 URL
    url = "http://192.168.0.152:2250/api/sendRobotInfo"  # 여기에 실제 서버 URL을 입력하세요

    # 보낼 데이터 (딕셔너리 형태로 작성)
    data = "robot1, robot111111111111111111111"
    
    
    while True:
        send_post_request(url, data)
        time.sleep(0.1)