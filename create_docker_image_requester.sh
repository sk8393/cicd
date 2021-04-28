#!/bin/bash
source ./create_docker_image_base02.sh
docker build -t sk8393/requester:test -f requester/Dockerfile .
if [ $? -ne 0 ]; then
    exit 1
fi
