FROM ros:galactic-ros-base-focal
ENV DEBIAN_FRONTEND=noninteractive

# setup sources.list
RUN echo "deb http://packages.ros.org/ros/ubuntu focal main" > /etc/apt/sources.list.d/ros1-latest.list

ENV ROS1_DISTRO noetic
ENV ROS2_DISTRO galactic

# Noetic key
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654
# Galactic key
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 4B63CF8FDE49746E98FA01DDAD19BAB3CBF125EA

# install ros packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-noetic-ros-base \
    ros-noetic-tf \
    && apt remove ros-galactic-ros1-bridge \
    && rm -rf /var/lib/apt/lists/*

ENV ROS_MASTER_URI=http://localhost:11311
ENV ROS_IP 127.0.0.1
ENV ROS_HOSTNAME localhost

ENV CMAKE_INSTALL_PREFIX=/usr/local

ENV ROS1_WORKSPACE=/root/ros1_ws
ENV ROS2_WORKSPACE=/root/ros2_ws

RUN mkdir -p $ROS1_WORKSPACE/src $ROS2_WORKSPACE/src

# Parameters for user to configure
ARG READ_TOKEN=<YOUR_TOKEN_HERE>
ARG NUM_THREADS=5

WORKDIR ${ROS1_WORKSPACE}

RUN git -C src clone https://oauth2:$READ_TOKEN@gitlab.gimrobotics.fi/mbari/inertial_sense_ros_msgs.git --depth 1 -b main

# Build ROS1 messages
RUN ldconfig && \
    . /opt/ros/noetic/setup.sh && \
    export MAKEFLAGS="-j${NUM_THREADS}" && \
    catkin_make_isolated --install

WORKDIR ${ROS2_WORKSPACE}

RUN git -C src clone https://oauth2:$READ_TOKEN@gitlab.gimrobotics.fi/mbari/inertial_sense_ros2_msgs.git --depth 1 -b main
RUN git -C src clone https://github.com/ros2/ros1_bridge.git --depth 1 -b galactic

# Build ROS2 messages
RUN ldconfig && \
    . /opt/ros/galactic/setup.sh && \
    export MAKEFLAGS="-j${NUM_THREADS}" && \
    colcon build --symlink-install --packages-select inertial_sense_ros2_msgs

# Build ros1_bridge
RUN ldconfig && \
    . /opt/ros/noetic/setup.sh && \
    . /opt/ros/galactic/setup.sh && \
    . /root/ros1_ws/install_isolated/setup.sh && \
    . /root/ros2_ws/install/local_setup.sh && \
    export MAKEFLAGS="-j${NUM_THREADS}" && \
    colcon build --packages-select ros1_bridge --cmake-force-configure

RUN printf 'source /opt/ros/galactic/setup.bash\n\
source /root/ros2_ws/install/local_setup.bash\n\
source /opt/ros/noetic/setup.bash\n\
source /root/ros1_ws/install_isolated/setup.bash' >> /root/.bashrc

CMD ["/bin/bash", "-i", "-c", "ros2 run ros1_bridge dynamic_bridge --bridge-all-topics"]
