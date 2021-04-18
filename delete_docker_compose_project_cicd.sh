#!/bin/bash
if [[ ${VARIABLES_LOADED} != "1" ]]
then
  source ./variables.sh
fi

set -euo pipefail

if [[ `whoami` != "root" ]]
then
  echo "$(printf "%${MAX_VARIABLE_LENGTH}s" "EXIT"): "Need to be root user to use docker command.""
  exit 1
fi

source jenkins/copy_config_file.sh
docker-compose -p cicd down
