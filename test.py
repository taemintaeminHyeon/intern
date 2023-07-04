from flask import Flask, render_template, request
from flask import jsonify
from operator import itemgetter



# run server
from flask_cors import CORS

app = Flask(__name__)   # Flask객체 할당
 
CORS(app, resources={r'*': {'origins': '*'}}) # 모든 곳에서 호출하는 것을 허용

savePoints = [{"robotID" : "null", "robotXP" : "0", "robotYP" : "0","robotZP" : "0"}]



# 이진 탐색
def binary_search(a, x):
    start = 0
    end = len(a) - 1

    while start <= end:
        mid = (start + end) // 2
        if x == a[mid]['robotID']:
            return mid
        elif x > a[mid]['robotID']:
            start = mid + 1
        else:
            end = mid - 1
    return 0
    

@app.route("/api/setRoboticsInfo", methods=['POST'])
def setInfo():
    params = request.get_json() # 전달된 json값을 저장
    ID = params["ID"] #json 중 ID 부분만 저장
    xP = params["xPosition"] #json 중 xPosition 부분만 저장
    yP = params["yPosition"] #json 중 yPosition 부분만 저장
    zP = params["zPosition"] #json 중 zPosition 부분만 저장 
    
    savePoints = sorted(savePoints, key=lamda savePoints: (savePoints['robotID'])) # value 값인 robotID 값으로 오름차순 정렬
    checkPoint = binary_search(savePoints, ID) # 탐색 결과 (해당 위치) 저장
    if(checkPoint) : # 해당 ID 값의 좌표를 수정
        savePoints[checkPoint] = {"robotID" : ID, "robotXP" : xP, "robotYP" : yP,"robotZP" : zP}  # 딕셔너리 수정하는 코드
    else : # 리스트의 해당 기기가 존재하지 않을 경우 추가
        savePoints.append({"robotID" : ID, "robotXP" : xP, "robotYP" : yP,"robotZP" : zP}) # 리스트에 딕셔너리 추가하는 코드
        
         

@app.route("/api/getRoboticsInfo", methods=['GET'])



def getInfo(): 
   
    json = {"xPosition" : xP, "yPosition" : yP, "zPosition" : zP}
    
    return jsonify(json)
    


# set,get 동시에 이루어져야하며, 각 기기에 독립적으로 작동되어야 한다.


    
app.run(host="0.0.0.0", port=2222) #서버 실행
#app.run() #로컬 테스트 확인용 














































































































