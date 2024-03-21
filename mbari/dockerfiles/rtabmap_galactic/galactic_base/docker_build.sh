#!/usr/bin/env bash

docker build -t mbari/galactic/base --build-arg NUM_THREADS=8 .
