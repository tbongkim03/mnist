from typing import Annotated
from fastapi import FastAPI, File, UploadFile
import os
import time
import pymysql
import pytz
from pytz import timezone
from datetime import datetime
app = FastAPI()


@app.post("/files/")
async def create_file(file: Annotated[bytes, File()]):
    return {"file_size": len(file)}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    # 파일 저장
    img = await file.read()
    file_name = file.filename
    file_exet = file.content_type.split('/')[-1]
    upload_dir = "/home/michael/code/mnist/img"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    import uuid
    file_full_path = os.path.join(upload_dir, f"{uuid.uuid4()}.{file_exet}")
    # 시간을 구함
    #from pytz import timezone
    #from datetime import datetime
    kst = pytz.timezone('Asia/Seoul')
    current_time_kst = datetime.now(kst)
    t = current_time_kst.strftime('%Y-%m-%d %H:%M:%S')
    with open(file_full_path, "wb") as f:
        f.write(img)
    # 파일 저장 경로 DB INSERT
    # tablename : image_processing
    # 컬럼 정보 : num (초기 인서트, 자동증가)
    # 처음 컬럼 정보 : 파일이름, 파일경로, 요청시간 (초기 인서트), 요청사용자(n00)
    # 컬럼 정보 : 예측모델, 예측결과, 예측시간 (추후 업데이트)
    from mnist.db import connect
    conn = connect()

    cursor = conn.cursor(pymysql.cursors.DictCursor)

    sql = "INSERT INTO image_processing(file_name, file_path, request_time, request_user) VALUES(%s, %s, %s, %s)"

    with conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (file_name, upload_dir, t, 'n13'))
        conn.commit()

    return {
            "filename": file.filename,
            "content_type":file.content_type
            }

@app.get("/one")
def one():
    from mnist.db import select
    sql = "SELECT * FROM image_processing WHERE prediction_time IS NULL ORDER BY num LIMIT 1"
    result = select(sql, size = 1) 

    return result[0]

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
