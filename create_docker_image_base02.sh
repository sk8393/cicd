#!/bin/bash
source ./create_docker_image_base01.sh
docker build -t sk8393/base02:2.0 -f base02/Dockerfile .
