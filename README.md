# Distributed-OpenPose
Distributed OpenPose aiming to run on servers only with CPUs.

## Notes
* Current implementation is only tested under Ubuntu 18
* Original OpenPose repo: https://github.com/CMU-Perceptual-Computing-Lab/openpose

## Instructions
1. Run the installation script to install all the dependencies on all servers
2. Start up kafka and Spark master/slaves
3. Run video_collector/producer.py
4. Run video_processor/frame_processor.py

## TODO
* Add docker support
* Use Kafka + Spark Streaming for stream processing


