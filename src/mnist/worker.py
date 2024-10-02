from mnist.db import select, dml
import random
import os
import requests

import time
import pytz
from pytz import timezone
from datetime import datetime

# predict
import numpy as np
from PIL import Image
from keras.models import load_model

def timer():
    kst = pytz.timezone('Asia/Seoul')
    current_time_kst = datetime.now(kst)
    t = current_time_kst.strftime('%Y-%m-%d %H:%M:%S')
    return t

# 사용자 이미지 불러오기 및 전처리
def preprocess_image(image_path):
    img = Image.open(image_path).convert('L')  # 흑백 이미지로 변환
    img = img.resize((28, 28))  # 크기 조정

    # 흑백 반전
    img = 255 - np.array(img)  # 흑백 반전

    img = np.array(img)
    img = img.reshape(1, 28, 28, 1)  # 모델 입력 형태에 맞게 변형
    img = img / 255.0  # 정규화
    return img

# 예측
def predict_digit(image_path):
    # 모델 로드
    path = os.path.dirname(__file__)
    file = '/mnist240924.keras'
    model = load_model(path+file)  # 학습된 모델 파일 경로

    img = preprocess_image(image_path)
    prediction = model.predict(img)
    digit = np.argmax(prediction)
    return digit

def get_job_img_task():
   sql = """
   SELECT
    num, file_name, file_path, label
   FROM image_processing
   WHERE prediction_result IS NULL
   ORDER BY num -- 가장 오래된 요청
   LIMIT 1 -- 하나씩
   """
   r = select(sql, 1)

   if len(r) > 0:
       return r[0]
   else:
       return None

def get_job_duration(num):
    sql = f"""
    SELECT
     prediction_time, request_time
    FROM image_processing
    WHERE num={num}
    """
    result = select(sql, 1)
    return result[0]

def prediction(file_path, num):
    sql = """UPDATE image_processing
    SET prediction_result=%s,
        prediction_model='n13',
        prediction_time=%s
    WHERE num=%s
    """
    # 예측 실행
    predicted_digit = predict_digit(file_path)
    #print("예측된 숫자:", predicted_digit)
    dml(sql, predicted_digit, timer(), num)

    return predicted_digit


def run():
  """image_processing 테이블을 읽어서 가장 오래된 요청 하나씩을 처리"""

  # STEP 1
  # image_processing 테이블의 prediction_result IS NULL 인 ROW 1 개 조회 - num 갖여오기
  job = get_job_img_task()

  if job is None:
      print(f"{timer()} - job is None")
      return

  num = job['num']
  file_name = job['file_name']
  label = job['label']
  file_path = job['file_path']

  # STEP 2
  # RANDOM 으로 0 ~ 9 중 하나 값을 prediction_result 컬럼에 업데이트
  # 동시에 prediction_model, prediction_time 도 업데이트
  prediction_result = prediction(file_path, num)
  job = get_job_duration(num)
  fmt = '%Y-%m-%d %H:%M:%S'

  prediction_time = datetime.strptime(job['prediction_time'], fmt)
  request_time = datetime.strptime(job['request_time'], fmt)
  dt = prediction_time - request_time
  total_seconds = dt.total_seconds()
  hours = int(total_seconds // 3600)
  minutes = int((total_seconds % 3600) // 60)
  seconds = int(total_seconds % 60)

  # 출력 형식을 맞추기 위해 시간, 분, 초 조건에 맞게 문자열 생성
  duration = ''
  if hours > 0:
    duration += f"{hours}시간 "
  if minutes > 0:
    duration += f"{minutes}분 "
  if seconds > 0:
    duration += f"{seconds}초"

  # STEP 3
  # LINE 으로 처리 결과 전송
  send_line_noti(file_name, label, prediction_result, duration)

  print(timer())

def send_line_noti(file_name, label, prediction_result, duration):
    api = "https://notify-api.line.me/api/notify"
    token = os.getenv('LINE_NOTI_TOKEN', 'NULL')
    if token == 'NULL':
       print("환경변수가 없어요")
    h = {'Authorization':'Bearer ' + token}
    mm = f"""
    🔢 숫자 예측 모델 결과 ⁉️
    파일명 : {file_name}
    라  벨 : {label}
    예  측 : {prediction_result}
    시  간 : {duration}
       """
    if int(label) == int(prediction_result):
        mm=mm+"""
    🙆 정확히 예측했어요! 😍
        """
    else:
        mm=mm+"""
    🤦 예측에 실패했어요.. 😰
    글씨를 굵게 써보는건 어떨까요?
        """
    msg = {
        "message" : mm
    }
    requests.post(api, headers=h , data=msg)
    print("SEND LINE NOTI")
