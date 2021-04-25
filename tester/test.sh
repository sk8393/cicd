#!/bin/bash
CONFIRM_CLUSTER_COMMAND='curl -s -X GET "elasticsearch:9200/_cat/health?format=json&pretty"'
# CONFIRM_CLUSTER_COMMAND='curl -s -X GET "elasticsearch:9200/_cat/health?v"'
echo "\$ ${CONFIRM_CLUSTER_COMMAND}"
eval ${CONFIRM_CLUSTER_COMMAND}

CONFIRM_INDEX_COMMAND='curl -s -X GET "elasticsearch:9200/_cat/indices/awssql*?format=json&pretty"'
# CONFIRM_INDEX_COMMAND='curl -s -X GET "elasticsearch:9200/_cat/indices/awssql*?v"'
echo "\$ ${CONFIRM_INDEX_COMMAND}"
eval ${CONFIRM_INDEX_COMMAND}
