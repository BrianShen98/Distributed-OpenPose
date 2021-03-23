import cv2
import sys
from kafka import KafkaConsumer
import json
import time
import numpy as np
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
# from pyspark.streaming import StreamingContext
# from pyspark.streaming.kafka import KafkaUtils

# timing start
start_time = time.time()  

# Create Kafka consumer
consumer = KafkaConsumer(
    'real_frame',
     bootstrap_servers=['10.138.0.2:9092'],
     auto_offset_reset='earliest',
     enable_auto_commit=True,
     group_id='my-group')

# Create spark session
master_url =  "spark://10.168.0.4:7077"
conf = SparkConf().setMaster(master_url) \
                  .setExecutorEnv("spark.executor.memory", "16g") \
                  .setExecutorEnv("spark.driver.memory", "14g") 

                  
spark = SparkSession.builder \
    .config(conf=conf) \
    .getOrCreate()

sc = spark.sparkContext
# 2 seconds window
# ssc = StreamingContext(sc, 1)

all_images = []
count = 0

for message in consumer:
  image = cv2.imdecode(np.frombuffer(message.value, dtype='uint8'), cv2.IMREAD_UNCHANGED)
  all_images.append((count, image))
  count += 1


def processImage(image_with_id):
  import sys
  sys.path.append("/usr/local/python")
  from openpose import pyopenpose as op
  
  params = dict()
  params["model_folder"] = "/usr/local/openpose/models/"

  # Starting OpenPose
  opWrapper = op.WrapperPython()
  opWrapper.configure(params)
  opWrapper.start()
  datum = op.Datum()
  # get the image as input to openpose
  datum.cvInputData = image_with_id[1]
  opWrapper.emplaceAndPop(op.VectorDatum([datum]))
  return (image_with_id[0],datum.cvOutputData)
  

sc = spark.sparkContext

num_frame_per_batch = 100
num_partition = 40
for i in range(len(all_images)//num_frame_per_batch + 1):
  current_batch = all_images[i*num_frame_per_batch : min((i+1)*num_frame_per_batch, len(all_images))]
  all_processed_images = sc.parallelize(current_batch, num_partition).map(lambda x : processImage(x)).sortByKey().collect()

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

