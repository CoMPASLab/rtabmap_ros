#!/usr/bin/env bash

docker build -t mbari/rtabmap_ros:latest --build-arg NUM_THREADS=16 --build-arg READ_TOKEN=$@ .