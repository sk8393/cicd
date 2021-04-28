#!/bin/bash
source ./create_docker_image_base01.sh
docker build -t sk8393/base02:test -f base02/Dockerfile .
if [ $? -ne 0 ]; then
    exit 1
fi
