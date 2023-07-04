# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 08:57:51 2023

@author: jbr
"""

from flask import Flask, render_template, request
from sqlalchemy import create_engine, text
import datetime
from sqlalchemy import create_engine
# run server
from flask_cors import CORS


engine = create_engine("mysql+mysqlconnector://root:1234@localhost/testdb")
app = Flask(__name__)   # Flask객체 할당
app.config.from_pyfile("config.py")
database = create_engine(app.config['DB_URL'], encoding='utf-8', max_overflow=0)
app.database = database
CORS(app, resources={r'*': {'origins': '*'}}) # 모든 곳에서 호출하는 것을 허용


@app.route("/api/setRoboticsInfo", methods=['POST'])
def setInfo():
    try:
        params = request.get_data() # 전달된 json값을 저장
        params = str(params, "utf-8")
        if params is '':
            return "Params is null"
        now = datetime.datetime.now()
    
        time = str(now.year)+'-'+str(now.month)+'-'+str(now.day)+' '+str(now.hour)+':'+str(now.minute)+':'+str(now.second) #1000-00-00 00:00:00
        with engine.connect() as connection:
            connection.execute("INSERT INTO info (data, date) VALUES (%s, %s)", (params, time))

        return "Success"
    
    except Exception as e:
        return "An error occurred : {}".format(str(e))
    
    



@app.route("/api/getRoboticsInfo", methods=['POST','GET'])
def getInfo(): 
    try:
        params = request.get_data() # 전달된 json값을 저장
        params = str(params, "utf-8")
        if params is '':
            return "Params is null"
        
        print(params)
        
        
        
        row = app.database.execute("""
                SELECT data
                FROM info 
                WHERE date = %s
            """, params).fetchone()

        return str(row)
    
    except Exception as e:
        return "An error occurred: {}".format(str(e))

# 콤마 제거 
    #if row:
    #    data = row[0]  # 첫 번째 요소인 data 값을 추출합니다.
    #    return str(data)  # data 값을 반환합니다.
    #else:
    #    return "No data found"
    
    


@app.route("/api/robotGo", methods=['POST'])
def sendGoInfo(): 
    params = request.get_data() # 전달된 json값을 저장
    params = str(params, "utf-8")
        
    return params+'Go'
    


@app.route("/api/robotStop", methods=['POST'])
def sendStopInfo(): 
    params = request.get_data() # 전달된 json값을 저장
    params = str(params, "utf-8")
           
    return params+'Stop'
        
    
    
app.run(host="0.0.0.0", port=2222) #서버 실행


