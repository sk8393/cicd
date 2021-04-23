#!/bin/bash
sysctl -w vm.max_map_count=262144
docker-compose -p cicd up -d
