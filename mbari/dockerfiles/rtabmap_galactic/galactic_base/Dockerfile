FROM ros:galactic-ros-base
ENV DEBIAN_FRONTEND=noninteractive

# Install apt dependencies
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:borglab/gtsam-release-4.0 && \
    apt-get install -y \
    wget \
    libgtsam-dev \
    libgtsam-unstable-dev \
    libboost-all-dev \
    libpcl-dev \
    libglib2.0-dev \
    libyaml-cpp-dev \
    ros-galactic-navigation2 \
    ros-galactic-robot-localization \
    ros-galactic-octomap-msgs \
    ros-galactic-pcl-conversions \
    ros-galactic-pcl-ros \
    ros-galactic-vision-msgs \
    ros-galactic-ament-cmake-clang-format \
    ros-galactic-rviz2 \
    ros-galactic-octomap \
    ros-galactic-octomap-mapping \
    python3-pip \
    python3-pcl \
    libqt5svg5-dev && \
    apt-get remove -y libopencv-core4.2 && \
    apt-get install -y ros-galactic-camera-info-manager

ENV CMAKE_INSTALL_PREFIX=/usr/local
ENV DEPS_DIR=/home/mbari/deps

WORKDIR ${DEPS_DIR}

ARG NUM_THREADS=5

# Clone, build, and install OpenCV with contrib modules @ 4.2.0
RUN git clone --depth 1 --branch 4.2.0 https://github.com/opencv/opencv.git && \
    git clone --depth 1 --branch 4.2.0 https://github.com/opencv/opencv_contrib && \
    cd opencv && \
    mkdir build && \
    cd build && \
    cmake \
    -D CMAKE_INSTALL_PREFIX=${CMAKE_INSTALL_PREFIX} \
    -D CMAKE_BUILD_TYPE=Release \
    -D OPENCV_ENABLE_NONFREE=1 \
    -D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules \
    .. && \
    make -j${NUM_THREADS} install && \
    make install && \
    cd ${DEPS_DIR}

# Clone, build, and install LCM @ v1.4.0
RUN git clone https://github.com/lcm-proj/lcm.git && \
    cd lcm && \
    git checkout v1.4.0 && \
    mkdir build && \
    cd build && \
    cmake \
    -D CMAKE_INSTALL_PREFIX=$CMAKE_INSTALL_PREFIX \
    -D CMAKE_BUILD_TYPE=Release \
    .. && \
    make -j${NUM_THREADS} install && \
    cd ${DEPS_DIR}

# Install python dependencies
RUN pip3 install rosbags open3d && \
    pip3 install --upgrade numpy

RUN echo "source /opt/ros/galactic/setup.bash" >> ~/.bashrc

WORKDIR /home/mbari/

RUN rm -rf /home/mbari/deps/
RUN mkdir -p /home/mbari/colcon_ws/src/
