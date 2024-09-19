from typing import Annotated
from fastapi import FastAPI, File, UploadFile
import os
app = FastAPI()


@app.post("/files/")
async def create_file(file: Annotated[bytes, File()]):
    return {"file_size": len(file)}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    # 파일 저장
    img = await file.read()
    file_name = file.filename
    upload_dir = "./photo"
    file_full_path = os.path.join(upload_dir, file_name)
    with open(file_full_path, "wb") as f:
        f.write(img)
    # 파일 저장 경로 DB INSERT
    # tablename : image_processing
    # 컬럼 정보 : num (초기 인서트, 자동증가)
    # 처음 컬럼 정보 : 파일이름, 파일경로, 요청시간 (초기 인서트), 요청사용자(n00)
    # 컬럼 정보 : 예측모델, 예측결과, 예측시간 (추후 업데이트)
    import pymysql.cursors
    db = pymysql.connect(
            host = os.getenv("DB_IP", "localhost"),
            user = 'char',
            passwd = '1234',
            db = 'chardb',
            charset = 'utf8',
            port = int(os.getenv("DB_PORT", "33306"))
    )

    cursor = db.cursor(pymysql.cursors.DictCursor)

    sql = "INSERT INTO charhistory(num, file_name, file_path, dt, quser, model, result, end_time) VALUES(%d, %s, %s, %s, %s, %s, %s, %s)"

    with db:
        with db.cursor() as cursor:
            cursor.execute(sql, ('n13', name, t))
        db.commit()

    return {
            "filename": file.filename,
            "content_type":file.content_type
            }
