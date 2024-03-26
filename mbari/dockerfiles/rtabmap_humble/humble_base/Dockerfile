FROM ros:humble-ros-base
ENV DEBIAN_FRONTEND=noninteractive

# Install apt dependencies
RUN apt-get update && \
    apt-get install -y \
        wget \
        vim \
        libboost-all-dev \
        libpcl-dev \
        libglib2.0-dev \
        libyaml-cpp-dev \
        ros-humble-robot-localization \
        ros-humble-octomap-msgs \
        ros-humble-octomap-msgs \
        ros-humble-pcl-conversions \
        ros-humble-pcl-ros \
        ros-humble-vision-msgs \
        ros-humble-ament-cmake-clang-format \
        ros-humble-rviz2 \
        ros-humble-nav2-msgs \
        ros-humble-octomap \
        ros-humble-octomap-mapping \
        python3-pip \
        python3-pcl \
        libqt5svg5-dev && \
    apt-get remove -y libopencv-core4.5d \
        gcc-11 && \
# Install Nvidia CUDA \
    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin && \
    mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600 && \
    wget https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda-repo-ubuntu2204-11-8-local_11.8.0-520.61.05-1_amd64.deb && \
    dpkg -i cuda-repo-ubuntu2204-11-8-local_11.8.0-520.61.05-1_amd64.deb && \
    cp /var/cuda-repo-ubuntu2204-11-8-local/cuda-*-keyring.gpg /usr/share/keyrings/ && \
    rm -f /cuda-repo-ubuntu2204-11-8-local_11.8.0-520.61.05-1_amd64.deb && \
    echo 'export PATH=/usr/local/cuda-11.8/bin${PATH:+:${PATH}}' >> ~/.bashrc && \
# Install more apt dependencies \
    apt-get update && \
    apt-get install -y cuda \
        ros-humble-camera-info-manager \
        gcc-10 \
        g++-10 \
        build-essential && \
    rm -rf /var/cuda-repo-ubuntu2204-11-8-local/ && \
    echo 'source /opt/ros/humble/setup.bash' >> ~/.bashrc && \
# Install Python packages \
    pip3 install --no-cache-dir rosbags open3d && \
    pip3 install --no-cache-dir --upgrade numpy && \
# Clean apt cache \
    apt-get clean

ENV CMAKE_INSTALL_PREFIX=/usr/local
ENV DEPS_DIR=/home/mbari/deps

WORKDIR ${DEPS_DIR}

ARG NUM_THREADS=5

# Clone, build, and install OpenCV with contrib modules @ 4.5.4
RUN git clone --depth 1 -b 4.5.4 https://github.com/opencv/opencv.git && \
    git clone --depth 1 -b 4.5.4 https://github.com/opencv/opencv_contrib && \
    cd opencv && \
    mkdir build && \
    cd build && \
    cmake \
    -D CMAKE_INSTALL_PREFIX=${CMAKE_INSTALL_PREFIX} \
    -D CMAKE_BUILD_TYPE=Release \
    -D OPENCV_ENABLE_NONFREE=1 \
    -D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules \
    -D CMAKE_C_COMPILER=/usr/bin/gcc-10 \
    -D WITH_CUDA=1 \
    .. && \
    make -j${NUM_THREADS} install && \
    make install && \
    cd ${DEPS_DIR} && \
# Clone, build, and install LCM @ v1.5.0 \
    git clone --depth 1 -b v1.5.0 https://github.com/lcm-proj/lcm.git && \
    cd lcm && \
    mkdir build && \
    cd build && \
    cmake \
    -D CMAKE_INSTALL_PREFIX=$CMAKE_INSTALL_PREFIX \
    -D CMAKE_BUILD_TYPE=Release \
    .. && \
    make -j${NUM_THREADS} install && \
    cd ${DEPS_DIR} && \
# Clone, build, and install GTSAM @ 0909c46339e0c604b0f26c8a67c7144c1358db4c \
    git clone https://github.com/borglab/gtsam.git && \
    cd gtsam && \
    git checkout 0909c46339e0c604b0f26c8a67c7144c1358db4c && \
    mkdir build && \
    cd build && \
    cmake \
    -D CMAKE_INSTALL_PREFIX=$CMAKE_INSTALL_PREFIX \
    -D CMAKE_BUILD_TYPE=Release \
    -D GTSAM_BUILD_WITH_MARCH_NATIVE=OFF \
    -D GTSAM_USE_SYSTEM_EIGEN=ON \
    -D GTSAM_BUILD_TESTS=OFF \
    -D GTSAM_BUILD_EXAMPLES_ALWAYS=OFF \
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
    . /opt/ros/humble/setup.sh && \
    export MAKEFLAGS="-j${NUM_THREADS}" && \
    colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release && \
    echo 'source /home/mbari/colcon_ws/install/setup.bash' >> ~/.bashrc && \
# Could not remove deps dir itself when it was still the WORKDIR \
    rm -rf /home/mbari/deps/
