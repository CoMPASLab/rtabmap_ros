FROM ros:noetic-ros-base
ENV DEBIAN_FRONTEND=noninteractive

# Install apt dependencies
RUN apt-get update && \
    apt-get install -y \
        wget \
        tmux \
        nano \
        vim \
        git \
        libudev-dev \
        libusb-1.0-0 \
        libusb-1.0-0-dev \
        libyaml-cpp-dev \
        sudo \
        ros-noetic-tf && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ARG NUM_THREADS=8
# Set the working directory (optional)
WORKDIR /home/compas/catkin_ws/src

# Clone Inertial Sense Repository
RUN . /opt/ros/noetic/setup.sh && \
    catkin_init_workspace && \
    git clone https://github.com/inertialsense/inertial-sense-ros.git &&\
    cd inertial-sense-ros/lib && \
    git clone https://github.com/inertialsense/inertial-sense-sdk.git && \
    cd inertial-sense-sdk && git checkout 952d452

# Run colcon build in workspace directory
WORKDIR /home/compas/catkin_ws
RUN sudo ldconfig && \
    . /opt/ros/noetic/setup.sh && \
    export MAKEFLAGS="-j${NUM_THREADS}" && \
    catkin_make -DCMAKE_BUILD_TYPE=Release

# Set the ROS environment variables
ENV ROS_DISTRO noetic
ENV ROS_MASTER_URI=http://localhost:11311
ENV ROS_IP 127.0.0.1
ENV ROS_HOSTNAME localhost

RUN printf 'source /opt/ros/noetic/setup.bash\n\
source /home/compas/catkin_ws/devel/setup.bash\n' >> /root/.bashrc

CMD ["/bin/bash", "-i", "-c", "roscore& rosrun inertial_sense_ros inertial_sense_node"]
