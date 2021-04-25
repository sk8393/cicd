#!/bin/bash
source ./create_docker_image_base02.sh
docker build -t sk8393/tester:test -f tester/Dockerfile .
