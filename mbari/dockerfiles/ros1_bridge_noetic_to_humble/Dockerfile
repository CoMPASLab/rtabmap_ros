FROM ubuntu:jammy
ENV DEBIAN_FRONTEND=noninteractive

ENV ROS1_DISTRO noetic
ENV ROS2_DISTRO humble

RUN apt update && apt install -y apt-utils gnupg2

# setup sources.list
RUN sh -c echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros1-latest.list

# Noetic key
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654

RUN apt update && apt install locales && \
locale-gen en_US en_US.UTF-8 && \
update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 && \
export LANG=en_US.UTF-8

RUN apt update && apt upgrade && apt install -y \
  build-essential \
  cmake \
  git \
  libacl1-dev \
  libtinyxml2-dev \
  libldap2-dev \
  libasio-dev \
  libeigen3-dev \
  python3-flake8 \
  python3-flake8-blind-except \
  python3-flake8-builtins \
  python3-flake8-class-newline \
  python3-flake8-comprehensions \
  python3-flake8-deprecated \
  python3-flake8-docstrings \
  python3-flake8-import-order \
  python3-flake8-quotes \
  python3-pip \
  python3-pytest \
  python3-pytest-cov \
  python3-pytest-repeat \
  python3-pytest-rerunfailures \
  python3-setuptools \
  wget

# Install colcon from PyPI, rather than apt packages
RUN python3 -m pip install -U colcon-common-extensions vcstool

# ROS2 installation

# Copy trimmed repos file (has visualization related packages removed)
COPY ros2-trimmed.repos /root/ros2-trimmed.repos

RUN mkdir -p ~/ros2_humble/src && \
cd ~/ros2_humble && \
# Use this if the trimmed file stops working
# vcs import --input https://raw.githubusercontent.com/ros2/ros2/humble/ros2.repos src
vcs import --input /root/ros2-trimmed.repos src

RUN cd ~/ros2_humble/ && \
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release

# ROS1 installation

RUN apt update && apt install -y ros-core-dev

RUN mkdir -p ~/ros1_bridge/src && \
cd ~/ros1_bridge/src && \
git clone https://github.com/ros2/ros1_bridge && \
cd ~/ros1_bridge && \
source ~/ros2_humble/install/local_setup.bash && \
colcon build --cmake-args -DCMAKE_BUILD_TYPE=Release

ENV ROS_MASTER_URI=http://localhost:11311
ENV ROS_IP 127.0.0.1
ENV ROS_HOSTNAME localhost

RUN printf 'source ~/ros2_humble/install/local_setup.bash\n\
source /opt/ros/noetic/setup.bash\n' >> /root/.bashrc

CMD ["/bin/bash", "-i", "-c", "ros2 run ros1_bridge dynamic_bridge"]
