#!/bin/bash
source ./create_docker_image_base00.sh
docker build -t sk8393/base01:2.0 -f base01/Dockerfile .
