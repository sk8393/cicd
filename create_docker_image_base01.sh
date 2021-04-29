#!/bin/bash
source ./create_docker_image_base00.sh
docker build -t sk8393/base01:test -f base01/Dockerfile .
if [ $? -ne 0 ]; then
    exit 1
fi
