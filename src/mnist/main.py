from typing import Annotated
from fastapi import FastAPI, File, UploadFile
import os
import pymysql

import time
import pytz
from pytz import timezone
from datetime import datetime

import json
app = FastAPI()

def timer():
    kst = pytz.timezone('Asia/Seoul')
    current_time_kst = datetime.now(kst)
    t = current_time_kst.strftime('%Y-%m-%d %H:%M:%S')
    return t

@app.post("/files/")
async def create_file():
    conn = pymysql.connect(
            host=os.getenv('DB_IP', 'localhost'),
            port = int(os.getenv("DB_PORT", "53306")),
            user = 'mnist',
            passwd = '1234',
            db = 'mnistdb',
            charset = 'utf8'
    )
    with conn:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM image_processing WHERE prediction_time IS NULL ORDER BY num"
            cursor.execute(sql)
            result = cursor.fetchall()
            print(result)

    return result 


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile, label: int, insert_loop: int = 1):
    # 파일 저장
    img = await file.read()
    file_name = file.filename
    file_exet = file.content_type.split('/')[-1]

    # 디렉토리가 없으면 오류, 코드에서 확인 및 만들기 추가
    upload_dir = os.getenv("UPLOAD_DIR", "/home/michael/code/mnist/img")
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    import uuid
    file_full_path = os.path.join(upload_dir, f"{uuid.uuid4()}.{file_exet}")
    # 시간을 구함
    #from pytz import timezone
    #from datetime import datetime
    with open(file_full_path, "wb") as f:
        f.write(img)
    # 파일 저장 경로 DB INSERT
    # tablename : image_processing
    # 컬럼 정보 : num (초기 인서트, 자동증가)
    # 처음 컬럼 정보 : 파일이름, 파일경로, 요청시간 (초기 인서트), 요청사용자(n00)
    # 컬럼 정보 : 예측모델, 예측결과, 예측시간 (추후 업데이트)
    sql = "INSERT INTO image_processing(file_name, label, file_path, request_time, request_user) VALUES(%s, %s, %s, %s, %s)"
    from mnist.db import dml

    insert_line = 0
    for _ in range(insert_loop):
        insert_row = dml(sql, file_name, label, file_full_path, timer(), 'n13')

    return {
            "filename": file.filename,
            "content_type": file.content_type,
            "file_full_path": file_full_path,
            "insert_row_cont": insert_row
           }

@app.get("/one")
def one():
    from mnist.db import select
    sql = "SELECT * FROM image_processing WHERE prediction_time IS NULL ORDER BY num LIMIT 1"
    result = select(sql, size = 1) 

    return result

@app.get("/many")
def many(size: int = -1):
    from mnist.db import select
    sql = "SELECT * FROM image_processing WHERE prediction_time IS NULL ORDER BY num"
    result = select(sql, size)
    
    return result

@app.get("/all")
def all():
    from mnist.db import select
    sql = "SELECT * FROM image_processing"
    result = select(query=sql, size=-1)
    return result
