#!/bin/bash
source ./create_docker_image_base02.sh
docker build -t sk8393/cloud9:test -f cloud9/Dockerfile .
if [ $? -ne 0 ]; then
    exit 1
fi
