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
    && rm -rf /var/lib/apt/lists/*

# install ros2 packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-galactic-tf2 \
    ros-galactic-ros1-bridge \
    && rm -rf /var/lib/apt/lists/*

ENV ROS_MASTER_URI=http://localhost:11311
ENV ROS_IP 127.0.0.1
ENV ROS_HOSTNAME localhost

RUN printf 'source /opt/ros/galactic/setup.bash\n\
source /opt/ros/noetic/setup.bash\n' >> /root/.bashrc

CMD ["/bin/bash", "-i", "-c", "ros2 run ros1_bridge dynamic_bridge"]
