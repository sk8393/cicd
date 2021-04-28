#!/bin/bash
docker build -t sk8393/base00:test -f base00/Dockerfile .
if [ $? -ne 0 ]; then
    exit 1
fi
