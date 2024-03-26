#!/usr/bin/env bash

docker build -t mbari/humble/base-with-cuda-11.8-and-opencv-4.5.4 --build-arg NUM_THREADS=8 --build-arg READ_TOKEN=$@ .
