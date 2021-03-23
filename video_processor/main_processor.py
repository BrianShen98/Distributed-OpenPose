import cv2
import sys
import time
from argparse import ArgumentParser

import numpy as np
from kafka import KafkaConsumer
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf

from .frame_processor import processImage

# from pyspark.streaming import StreamingContext
# from pyspark.streaming.kafka import KafkaUtils

# Parse command line arguments
parser = ArgumentParser()
parser.add_argument("-s", "--spark_master_url", dest="spark_master_url",
                  help="specify the spark master's url")
parser.add_argument("-k", "--kafka_server_url", dest="kafka_server_url",
                  help="specify the kafka bootstrap server's url")                                 
args = parser.parse_args()

if not args.spark_master_url or not args.kafka_server_url:
  parser.print_help(sys.stderr)
  sys.exit(2)

spark_master_url = args.spark_master_url
kafka_server_url = args.kafka_server_url

# timing start
start_time = time.time()  

# Create Kafka consumer
consumer = KafkaConsumer(
    'real_frame',
     bootstrap_servers=[kafka_server_url],
     auto_offset_reset='earliest',
     enable_auto_commit=True,
     group_id='my-group')

# Create spark session
master_url =  spark_master_url
conf = SparkConf().setMaster(master_url) \
                  .setExecutorEnv("spark.executor.memory", "16g") \
                  .setExecutorEnv("spark.driver.memory", "14g") 

                  
spark = SparkSession.builder \
    .config(conf=conf) \
    .getOrCreate()

sc = spark.sparkContext
# 2 seconds window
# ssc = StreamingContext(sc, 1)

# Read all frames from Kafka
all_images = []
count = 0

for message in consumer:
  image = cv2.imdecode(np.frombuffer(message.value, dtype='uint8'), cv2.IMREAD_UNCHANGED)
  all_images.append((count, image))
  count += 1

# Process frames
sc = spark.sparkContext
num_frame_per_batch = 100
num_partition = 40
for i in range(len(all_images)//num_frame_per_batch + 1):
  current_batch = all_images[i*num_frame_per_batch : min((i+1)*num_frame_per_batch, len(all_images))]
  all_processed_images = sc.parallelize(current_batch, num_partition) \
                            .map(lambda x : processImage(x)) \
                            .sortByKey() \
                            .collect()

  #output as video chunk
  height, width, layers = all_processed_images[0][1].shape
  video = cv2.VideoWriter("output_5_worker_{}.mp4".format(i), cv2.VideoWriter_fourcc(*'MP4V'), 20, (width,height))
  for img in all_processed_images:
    video.write(img[1])

end_time = time.time()

# write time to a file
original_stdout = sys.stdout # Save a reference to the original standard output

with open('timing.txt', 'a') as f:
    sys.stdout = f # Change the standard output to the file we created.
    print('Timing for five  machine: {}'.format(end_time-start_time))
    sys.stdout = original_stdout # Reset the standard output to its original value
    
# Release everything if job is finished
video.release()
cv2.destroyAllWindows()

print("5 workers elasped time:{}".format(end_time - start_time))

