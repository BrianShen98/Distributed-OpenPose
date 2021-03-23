import sys
from datetime import datetime
from argparse import ArgumentParser

import cv2
from kafka import KafkaProducer

# Parse command line arguments
parser = ArgumentParser()
parser.add_argument("-v", "--video", dest="video_name",
                  help="specify the video to be processed")
parser.add_argument("-k", "--kafka_server_url", dest="kafka_server_url",
                  help="specify the kafka bootstrap server's url") 
args = parser.parse_args()

if not args.video_name or not args.kafka_server_url:
      parser.print_help(sys.stderr)
      sys.exit(2)

video_name = args.video_name
kafka_server_url = args.kafka_server_url

# Create Kafka Producer
producer = KafkaProducer(bootstrap_servers=[kafka_server_url])

# Process video and send frames to Kafka
vidcap = cv2.VideoCapture(video_name)
count = 0
all_images=[]
success,image = vidcap.read()

while success:
      count += 1
      producer.send("real_frame",cv2.imencode(".jpg",image)[1].tobytes())
      success,image = vidcap.read()

print(count)
producer.flush()
