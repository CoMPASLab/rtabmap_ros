FROM ros:galactic-ros-base
ENV DEBIAN_FRONTEND=noninteractive

# Install apt dependencies
RUN apt-get update && \
    apt-get install -y \
        wget \
        libboost-all-dev \
        libpcl-dev \
        libglib2.0-dev \
        ros-galactic-navigation2 \
        ros-galactic-image-proc \
        ros-galactic-robot-localization \
        ros-galactic-octomap-msgs \
        ros-galactic-pcl-conversions && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV CMAKE_INSTALL_PREFIX=/usr/local
ENV DEPS_DIR=/root/deps

WORKDIR ${DEPS_DIR}

ARG NUM_THREADS=1

# Clone, build, and install GTSAM @ 0909c46339e0c604b0f26c8a67c7144c1358db4c
RUN git clone https://github.com/borglab/gtsam.git && \
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
    cd ${DEPS_DIR} && rm -rf gtsam

# Clone, build, and install OpenCV @ 4.7.0
RUN git clone https://github.com/opencv/opencv.git && \
    cd opencv && \
    git checkout 4.7.0 && \
    mkdir build && \
    cd build && \
    cmake \
        -D CMAKE_INSTALL_PREFIX=${CMAKE_INSTALL_PREFIX} \
        -D CMAKE_BUILD_TYPE=Release \
        .. && \
    make -j${NUM_THREADS} install && \
    make install && \
    cd ${DEPS_DIR} && \
    rm -rf opencv

# Clone, build, and install libnabo @ 3cab7eed92bd5d4aed997347b8c8a2692a83a532
RUN git clone https://github.com/ethz-asl/libnabo.git && \
    cd libnabo && \
    git checkout 3cab7eed92bd5d4aed997347b8c8a2692a83a532 && \
    mkdir build && \
    cd build && \
    cmake \
        -D CMAKE_INSTALL_PREFIX=$CMAKE_INSTALL_PREFIX \
        -D CMAKE_BUILD_TYPE=Release \
        .. && \
    make -j${NUM_THREADS} install && \
    cd ${DEPS_DIR} && rm -rf libnabo

# Clone, build, and install libpointmatcher @ 76f99fce0fe69e6384102a0343fdf8d262626e1f
RUN git clone https://github.com/ethz-asl/libpointmatcher.git && \
    cd libpointmatcher && \
    git checkout 76f99fce0fe69e6384102a0343fdf8d262626e1f && \
    mkdir build && \
    cd build && \
    cmake \
        -D CMAKE_INSTALL_PREFIX=$CMAKE_INSTALL_PREFIX \
        -D CMAKE_BUILD_TYPE=Release \
        .. && \
    make -j${NUM_THREADS} install && \
    cd ${DEPS_DIR} && rm -rf libpointmatcher

# Clone, build, and install OpenGV @ 91f4b19c73450833a40e463ad3648aae80b3a7f3
RUN git clone https://github.com/laurentkneip/opengv.git && \
    cd opengv && \
    git checkout 91f4b19c73450833a40e463ad3648aae80b3a7f3 && \
    wget https://gist.githubusercontent.com/matlabbe/a412cf7c4627253874f81a00745a7fbb/raw/accc3acf465d1ffd0304a46b17741f62d4d354ef/opengv_disable_march_native.patch && \
    git apply opengv_disable_march_native.patch && \
    mkdir build && \
    cd build && \
    cmake \
        -D CMAKE_INSTALL_PREFIX=$CMAKE_INSTALL_PREFIX \
        -D CMAKE_BUILD_TYPE=Release \
        .. && \
    make -j${NUM_THREADS} install && \
    cd ${DEPS_DIR} && rm -rf opengv

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
    cd ${DEPS_DIR} && rm -rf lcm

# Set the working directory
WORKDIR /root/rtabmap_ws/src

ARG READ_TOKEN

# Clone rtabmap (develop branch)
RUN git clone https://oauth2:${READ_TOKEN}@gitlab.gimrobotics.fi/mbari/rtabmap.git -b develop

# Clone rtabmap_ros (mbari branch)
RUN git clone https://oauth2:${READ_TOKEN}@gitlab.gimrobotics.fi/mbari/rtabmap_ros.git -b mbari

# Clone lcm_to_ros (ros2 branch)
RUN git clone https://oauth2:${READ_TOKEN}@gitlab.gimrobotics.fi/mbari/lcm_to_ros.git -b ros2

# Run colcon build in workspace directory
WORKDIR /root/rtabmap_ws
RUN ldconfig && \
    . /opt/ros/galactic/setup.sh && \
    export MAKEFLAGS="-j${NUM_THREADS}" && \
    colcon build --symlink-install

# Create the RTAB-Map output directory
RUN mkdir /root/rtab_out
