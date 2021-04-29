#!/bin/bash
# Check record is inserted in PostgreSQL.
CONFIRM_RECORD_COMMAND='psql -h postgres -U root -d awssql -t -A -c "SELECT * FROM root.ec2_describe_instances_instances ORDER BY _timestamp DESC LIMIT 1;"'
NUMBER_OF_RECORD=`eval "${CONFIRM_RECORD_COMMAND} | wc -l"`
if [ ${NUMBER_OF_RECORD} -ne 1 ]; then
  echo "\$ ${CONFIRM_RECORD_COMMAND} | wc -l"
  eval "${CONFIRM_RECORD_COMMAND} | wc -l"
  exit 1
else
  echo "\$ ${CONFIRM_RECORD_COMMAND}"
  eval "${CONFIRM_RECORD_COMMAND}"
fi

# Confirm status of Elasticsearch cluster.
CONFIRM_CLUSTER_COMMAND='curl -s -X GET "elasticsearch:9200/_cat/health?format=json&pretty"'
# CONFIRM_CLUSTER_COMMAND='curl -s -X GET "elasticsearch:9200/_cat/health?v"'
echo "\$ ${CONFIRM_CLUSTER_COMMAND}"
eval ${CONFIRM_CLUSTER_COMMAND}

CONFIRM_INDEX_COMMAND='curl -s -X GET "elasticsearch:9200/_cat/indices/awssql*?format=json&pretty"'
# CONFIRM_INDEX_COMMAND='curl -s -X GET "elasticsearch:9200/_cat/indices/awssql*?v"'
RETRIEVE_LENGTH_OF_ARRAY=' | jq ". | length"'

# Confirm expected index is registered on Elasticsearch.
COUNT=1
while :;
do
  NUMBER_OF_INDEX=`eval "${CONFIRM_INDEX_COMMAND}${RETRIEVE_LENGTH_OF_ARRAY}"`
  if [ ${NUMBER_OF_INDEX} -gt 0 ]; then
    echo "\$ ${CONFIRM_INDEX_COMMAND}"
    eval "${CONFIRM_INDEX_COMMAND}"
    break
  else
    echo "\$ ${CONFIRM_INDEX_COMMAND}${RETRIEVE_LENGTH_OF_ARRAY}"
    eval "${CONFIRM_INDEX_COMMAND}${RETRIEVE_LENGTH_OF_ARRAY}"
  fi

  if [ ${COUNT} -eq 12 ]; then
    exit 1
  fi

  sleep 10

  (( COUNT++ ))
done

exit 0
