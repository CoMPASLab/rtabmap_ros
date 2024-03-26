FROM ros:galactic-ros-base
ENV DEBIAN_FRONTEND=noninteractive

# Install apt and python dependencies
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
    apt-get install -y ros-galactic-camera-info-manager && \
    pip3 install --no-cache-dir rosbags open3d && \
    pip3 install --no-cache-dir --upgrade numpy && \
    apt-get clean && \
    echo 'source /opt/ros/galactic/setup.bash' >> ~/.bashrc

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
    cd ${DEPS_DIR} && \
# Clone, build, and install LCM @ v1.4.0 \
    git clone https://github.com/lcm-proj/lcm.git && \
    cd lcm && \
    git checkout v1.4.0 && \
    mkdir build && \
    cd build && \
    cmake \
    -D CMAKE_INSTALL_PREFIX=$CMAKE_INSTALL_PREFIX \
    -D CMAKE_BUILD_TYPE=Release \
    .. && \
    make -j${NUM_THREADS} install && \
    cd /home/mbari/ && \
    rm -rf /home/mbari/deps/

ARG READ_TOKEN=<YOUR_TOKEN_HERE>

WORKDIR /home/mbari/

# Clone and build MBARI rtabmap msgs (main branch)
RUN mkdir -p colcon_ws/src/ && \
    cd colcon_ws/src && \
    git clone --depth 1 -b main https://oauth2:$READ_TOKEN@gitlab.gimrobotics.fi/mbari/mbari_rtabmap_msgs.git && \
    cd .. && \
    . /opt/ros/galactic/setup.sh && \
    export MAKEFLAGS="-j${NUM_THREADS}" && \
    colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release && \
    echo 'source /home/mbari/colcon_ws/install/setup.bash' >> ~/.bashrc && \
# Could not remove deps dir itself when it was still the WORKDIR \
    rm -rf /home/mbari/deps/
