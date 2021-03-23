# This script is for installing all the necessary dependency on remote servers.
# Assuming the OS is Ubuntu 18

#!/bin/bash
echo "install new CMake becaue of CUDA10"

wget -q https://cmake.org/files/v3.13/cmake-3.13.0-Linux-x86_64.tar.gz
sudo tar xfz cmake-3.13.0-Linux-x86_64.tar.gz --strip-components=1 -C /usr/local

echo "clone openpose"
sudo git clone -q --depth 1 https://github.com/CMU-Perceptual-Computing-Lab/openpose.git /usr/local/openpose

echo "install cuda"

CUDA_PIN_LINK=https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/cuda-ubuntu1804.pin
CUDA_LINK=http://developer.download.nvidia.com/compute/cuda/10.2/Prod/local_installers/cuda-repo-ubuntu1804-10-2-local-10.2.89-440.33.01_1.0-1_amd64.deb
echo "wget -c \"$CUDA_PIN_LINK\" ${WGET_VERBOSE}"
wget -c $CUDA_PIN_LINK ${WGET_VERBOSE}
sudo mv cuda-ubuntu1804.pin /etc/apt/preferences.d/cuda-repository-pin-600
echo "wget \"$CUDA_LINK\" ${WGET_VERBOSE}"
wget $CUDA_LINK ${WGET_VERBOSE}
sudo dpkg -i cuda-repo-ubuntu1804-10-2-local-10.2.89-440.33.01_1.0-1_amd64.deb
sudo apt-key add /var/cuda-repo-10-2-local-10.2.89-440.33.01/7fa2af80.pub
sudo apt-get update

sudo DEBIAN_FRONTEND=noninteractive apt-get -yq install cuda

echo "finish cuda"

echo "install cuDNN"
CUDNN_LINK=http://developer.download.nvidia.com/compute/redist/cudnn/v7.6.5/cudnn-10.2-linux-x64-v7.6.5.32.tgz
wget -c $CUDNN_LINK ${WGET_VERBOSE}

sudo tar -xzf cudnn-10.2-linux-x64-v7.6.5.32.tgz -C /usr/local
rm cudnn-10.2-linux-x64-v7.6.5.32.tgz && sudo ldconfig

echo "install opencv"
# sudo apt-get -y install libopencv-dev
echo "install system dependencies"
sudo bash /usr/local/openpose/scripts/ubuntu/install_deps.sh
# python3 -m pip install --upgrade numpy protobuf opencv-python
echo "build openpose"
cd /usr/local/openpose && sudo rm -rf build || true && sudo mkdir build && cd build && sudo cmake -DBUILD_PYTHON=ON -DGPU_MODE=CPU_ONLY ..  && sudo make -j`nproc` && sudo make install


echo "install spark"

#install java
sudo apt install default-jdk scala git -y
#install spark
sudo wget https://downloads.apache.org/spark/spark-3.0.2/spark-3.0.2-bin-hadoop2.7.tgz
sudo tar xvf spark-*
sudo mv spark-3.0.2-bin-hadoop2.7 /opt/spark
echo "export SPARK_HOME=/opt/spark" >> ~/.profile
echo "export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin" >> ~/.profile
echo "export PYSPARK_PYTHON=/usr/bin/python3" >> ~/.profile
source .profile

# install pyspark
pip3 install pyspark

#start master
# sudo /opt/spark/sbin/start-master.sh

#start slave
# sudo /opt/spark/sbin/start-slave.sh spark://<master_ip>:7077