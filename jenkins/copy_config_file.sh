#!/bin/bash
if [[ ${VARIABLES_LOADED} != "1" ]]
then
  source ../variables.sh
fi

set -euo pipefail

if [[ `whoami` != "root" ]]
then
  echo "$(printf "%${MAX_VARIABLE_LENGTH}s" "EXIT"): "Need to be root user to use docker command.""
  exit 1
fi

# After introducing 'production' tag for Docker image, it should be relfected below.
NUMBER_OF_RUNNING_JENKINS_CONTAINER=`docker ps -a | grep -c jenkins`
echo "$(printf "%${MAX_VARIABLE_LENGTH}s" "NUMBER_OF_RUNNING_JENKINS_CONTAINER"): ${NUMBER_OF_RUNNING_JENKINS_CONTAINER}"
if [[ ${NUMBER_OF_RUNNING_JENKINS_CONTAINER} != "1" ]]
then
  echo "$(printf "%${MAX_VARIABLE_LENGTH}s" "EXIT"): "Only one Jenkins container is expected to be running.""
  exit 1
fi
JENKINS_IMAGE_ID=`docker ps -a | grep jenkins | cut -d " " -f1 | xargs docker inspect --format='{{.Image}}' | cut -d ':' -f2`
echo "$(printf "%${MAX_VARIABLE_LENGTH}s" "JENKINS_IMAGE_ID"): ${JENKINS_IMAGE_ID}"
JENKINS_IMAGE_NAME=`docker ps -a | grep jenkins | cut -d " " -f1 | xargs docker inspect --format='{{.Config.Image}}'`
echo "$(printf "%${MAX_VARIABLE_LENGTH}s" "JENKINS_IMAGE_NAME"): ${JENKINS_IMAGE_NAME}"
TIMESTAMP=`date +%s`
echo "$(printf "%${MAX_VARIABLE_LENGTH}s" "TIMESTAMP"): ${TIMESTAMP}"

# If there was a config.xml like below:
# jenkins/config-file-to-import/5bbc9ce244658c2a85a4d40f6caa3989f56dbfa9cc6d205b06b9e32e9ce172d0/1618493339/sample-export-config-file-20210415/config.xml
# Remove directory from timestamp part, and just keep following directory:
# jenkins/config-file-to-import/5bbc9ce244658c2a85a4d40f6caa3989f56dbfa9cc6d205b06b9e32e9ce172d0
REMOVE_CONFIG_FILE_COMMAND="rm -fR ${JENKINS_IMPORT_BASE_DIRECTORY}/${JENKINS_IMAGE_ID}"
echo "$(printf "%${MAX_VARIABLE_LENGTH}s" "REMOVE_CONFIG_FILE_COMMAND"): ${REMOVE_CONFIG_FILE_COMMAND}"
eval ${REMOVE_CONFIG_FILE_COMMAND}
echo "$(printf "%${MAX_VARIABLE_LENGTH}s" "\$?"): $?"

# Then create new directory like below with current timestamp:
# jenkins/config-file-to-import/5bbc9ce244658c2a85a4d40f6caa3989f56dbfa9cc6d205b06b9e32e9ce172d0/1618546531
#
#   1618493339: 2021-04-15 13:28:59
#   1618546531: 2021-04-16 04:15:31
#
# "5bbc9ce24465..." part can change if Docker image of Jenkins is different.
# This logic assures only one config file set per Docker image of Jenkins, and timestamp allows us to identify the latest one.

INDEX=0
# Copy config.xml under JENKINS_EXPORT_BASE_DIRECTORY, directory exposed from Jenkins container (/root/export) to JENKINS_IMPORT_BASE_DIRECTORY on host server.
for x in `find ${JENKINS_EXPORT_BASE_DIRECTORY} -name config.xml`
do
  EXPORTED_CONFIG_FILE=${x}
  echo "$(printf "%${MAX_VARIABLE_LENGTH}s" "EXPORTED_CONFIG_FILE[${INDEX}]"): ${EXPORTED_CONFIG_FILE}"
  JOB_NAME=`echo ${EXPORTED_CONFIG_FILE} | rev | cut -d '/' -f2 | rev`
  echo "$(printf "%${MAX_VARIABLE_LENGTH}s" "JOB_NAME[${INDEX}]"): ${JOB_NAME}"
  MAKE_DIRECTORY_FOR_CONFIG_FILE_COMMAND="mkdir -p ${JENKINS_IMPORT_BASE_DIRECTORY}/${JENKINS_IMAGE_ID}/${TIMESTAMP}/${JOB_NAME}"
  echo "$(printf "%${MAX_VARIABLE_LENGTH}s" "MAKE_DIRECTORY_FOR_CONFIG_FILE_COMMAND[${INDEX}]"): ${MAKE_DIRECTORY_FOR_CONFIG_FILE_COMMAND}"
  eval ${MAKE_DIRECTORY_FOR_CONFIG_FILE_COMMAND}
  echo "$(printf "%${MAX_VARIABLE_LENGTH}s" "\$?"): $?"
  COPY_CONFIG_FILE_COMMAND="cp ${EXPORTED_CONFIG_FILE} ${JENKINS_IMPORT_BASE_DIRECTORY}/${JENKINS_IMAGE_ID}/${TIMESTAMP}/${JOB_NAME}/"
  echo "$(printf "%${MAX_VARIABLE_LENGTH}s" "COPY_CONFIG_FILE_COMMAND[${INDEX}]"): ${COPY_CONFIG_FILE_COMMAND}"
  eval ${COPY_CONFIG_FILE_COMMAND}
  echo "$(printf "%${MAX_VARIABLE_LENGTH}s" "\$?"): $?"

  INDEX=$((${INDEX} + 1))
done
