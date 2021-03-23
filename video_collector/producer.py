from kafka import KafkaProducer
from time import sleep
import json
from datetime import datetime
import cv2

vidcap = cv2.VideoCapture('1min_30sec.mp4')
count = 0
all_images=[]
success,image = vidcap.read()

producer = KafkaProducer(bootstrap_servers=['localhost:9092'])

while success:
      count += 1
      producer.send("real_frame",cv2.imencode(".jpg",image)[1].tobytes())
      success,image = vidcap.read()

print(count)

producer.flush()
