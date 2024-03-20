FROM ros:humble-ros-base
ENV DEBIAN_FRONTEND=noninteractive

ARG USER_ID
ARG GROUP_ID

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
    python3-pip \
    python3-pcl \
    libqt5svg5-dev && \
    apt-get remove -y libopencv-core4.5d && \
    apt-get install -y ros-humble-camera-info-manager

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
    .. && \
    make -j${NUM_THREADS} install && \
    make install && \
    cd ${DEPS_DIR} && \
    rm -rf opencv

# Clone, build, and install LCM @ v1.5.0
RUN git clone --depth 1 -b v1.5.0 https://github.com/lcm-proj/lcm.git && \
    cd lcm && \
    mkdir build && \
    cd build && \
    cmake \
    -D CMAKE_INSTALL_PREFIX=$CMAKE_INSTALL_PREFIX \
    -D CMAKE_BUILD_TYPE=Release \
    .. && \
    make -j${NUM_THREADS} install && \
    cd ${DEPS_DIR} && rm -rf lcm

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

# Install python dependencies
RUN pip3 install rosbags open3d && \
    pip3 install --upgrade numpy

# Create and set the working directory
WORKDIR /home/mbari/rtabmap_ws/src

ARG READ_TOKEN=<YOUR_TOKEN_HERE>

# Clone ROS2 OpenCV libraries (need to be built against the locally installed OpenCV)
RUN git clone --depth 1 -b humble https://github.com/ros-perception/vision_opencv

# Clone ROS2 image pipeline libraries
RUN git clone --depth 1 -b humble https://github.com/ros-perception/image_pipeline

# Clone point_cloud_accumulator (main branch)
RUN git clone --depth 1 -b main https://oauth2:$READ_TOKEN@gitlab.gimrobotics.fi/mbari/point_cloud_accumulator.git

# Clone rtabmap (develop branch)
RUN git clone --depth 1 -b develop https://oauth2:$READ_TOKEN@gitlab.gimrobotics.fi/mbari/rtabmap.git

# Clone rtabmap_ros (mbari branch)
RUN git clone --depth 1 -b mbari https://oauth2:$READ_TOKEN@gitlab.gimrobotics.fi/mbari/rtabmap_ros.git

# Clone lcm_to_ros (ros2 branch)
RUN git clone --depth 1 -b ros2 https://oauth2:$READ_TOKEN@gitlab.gimrobotics.fi/mbari/lcm_to_ros.git

# Run colcon build in workspace directory
WORKDIR /home/mbari/rtabmap_ws

RUN . /opt/ros/humble/setup.sh && \
    export MAKEFLAGS="-j${NUM_THREADS}" && \
    colcon build --packages-select cv_bridge --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release &&  \
    . /home/mbari/rtabmap_ws/install/local_setup.sh && \
    colcon build --packages-skip cv_bridge --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release

WORKDIR /home/mbari/
USER root
RUN mkdir ./rtab_out

RUN cp /root/.bashrc ./.bashrc
RUN echo "source /opt/ros/humble/setup.bash" >> ./.bashrc
RUN echo "source /home/mbari/rtabmap_ws/install/local_setup.bash --extend" >> ./.bashrc

RUN addgroup --gid $GROUP_ID mbari
RUN adduser --disabled-password --gecos '' --uid $USER_ID --gid $GROUP_ID mbari

RUN chown -R mbari:mbari ./
USER mbari

# Expose VNC and Rviz port, may not be needed
EXPOSE 5900
EXPOSE 11311
