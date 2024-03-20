FROM ros:galactic-ros-base
ENV DEBIAN_FRONTEND=noninteractive

ARG USER_ID
ARG GROUP_ID

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
    cd ${DEPS_DIR} && \
    rm -rf opencv

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

# Install python dependencies
RUN pip3 install rosbags open3d && \
    pip3 install --upgrade numpy

# Add user before cloning and building. Could be added later and ws chowned to mbari, too.
RUN addgroup --gid $GROUP_ID mbari
RUN adduser --disabled-password --gecos '' --uid $USER_ID --gid $GROUP_ID mbari
USER mbari

# Set the working directory
WORKDIR /home/mbari/rtabmap_ws/src

ARG READ_TOKEN

# Clone ROS2 OpenCV libraries (need to be built against the locally installed OpenCV)
RUN git clone https://github.com/ros-perception/vision_opencv -b galactic

# Clone ROS2 image pipeline libraries and checkout to earlier non-broken commit
RUN git clone https://github.com/ros-perception/image_pipeline -b galactic && \
    cd image_pipeline && git checkout 46adf83e4854 && cd ..

# Clone point_cloud_accumulator (main branch)
RUN git clone https://oauth2:$READ_TOKEN@gitlab.gimrobotics.fi/mbari/point_cloud_accumulator.git -b main

# Clone rtabmap (develop branch)
RUN git clone https://oauth2:$READ_TOKEN@gitlab.gimrobotics.fi/mbari/rtabmap.git -b develop

# Clone rtabmap_ros (mbari branch)
RUN git clone https://oauth2:$READ_TOKEN@gitlab.gimrobotics.fi/mbari/rtabmap_ros.git -b mbari

# Clone lcm_to_ros (ros2 branch)
RUN git clone https://oauth2:$READ_TOKEN@gitlab.gimrobotics.fi/mbari/lcm_to_ros.git -b ros2

# Run colcon build in workspace directory
WORKDIR /home/mbari/rtabmap_ws

RUN . /opt/ros/galactic/setup.sh && \
    export MAKEFLAGS="-j${NUM_THREADS}" && \
    colcon build --packages-select cv_bridge --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release &&  \
    . /home/mbari/rtabmap_ws/install/local_setup.sh && \
    colcon build --packages-skip cv_bridge --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release

WORKDIR /home/mbari/
USER root
RUN mkdir rtab_out

RUN echo "source /opt/ros/galactic/setup.bash" >> .bashrc
RUN echo "source /home/mbari/rtabmap_ws/install/local_setup.bash --extend" >> .bashrc

RUN chown mbari:mbari rtab_out
RUN chown mbari:mbari .bashrc
RUN chown -R mbari:mbari deps/
RUN chown mbari:mbari .
USER mbari

# Expose VNC and Rviz port, may not be needed
EXPOSE 5900
EXPOSE 11311