#!/usr/bin/env bash

docker build -t mbari/humble/rtabmap_ros:latest \
    --build-arg NUM_THREADS=8 \
    --build-arg READ_TOKEN=$@ \
	--build-arg USER_ID=$(id -u) \
	--build-arg GROUP_ID=$(id -g) .