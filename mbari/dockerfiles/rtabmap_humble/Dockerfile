FROM mbari/humble/base-with-cuda-11.8-and-opencv-4.5.4:latest
ENV DEBIAN_FRONTEND=noninteractive

ARG USER_ID
ARG GROUP_ID
ARG READ_TOKEN=<YOUR_TOKEN_HERE>
ARG NUM_THREADS=5

WORKDIR /home/mbari/colcon_ws/src/

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
WORKDIR /home/mbari/colcon_ws

RUN . /opt/ros/humble/setup.sh && \
    export MAKEFLAGS="-j${NUM_THREADS}" && \
    colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release

WORKDIR /home/mbari/
USER root
RUN mkdir ./rtab_out

RUN cp ~/.bashrc ./.bashrc
RUN echo "source /home/mbari/colcon_ws/install/setup.bash" >> ./.bashrc

RUN addgroup --gid $GROUP_ID mbari
RUN adduser --disabled-password --gecos '' --uid $USER_ID --gid $GROUP_ID mbari

RUN chown -R mbari:mbari ./
USER mbari

# Expose VNC and Rviz port, may not be needed
EXPOSE 5900
EXPOSE 11311
