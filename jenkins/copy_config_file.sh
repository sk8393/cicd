#!/bin/bash
IMPORT_BASE_DIRECTORY="jenkins/config-file-to-import"
EXPORTED_BASE_DIRECTORY="jenkins/container-data-exported-config-file"

# Following image ID extraction might cause a problem if multiple Jenkins containers are running.
# After introducing 'production' tag for Docker image, it should be relfected below.
JENKINS_IMAGE_ID=`docker ps -a | grep jenkins | cut -d " " -f1 | xargs docker inspect --format='{{.Image}}' | cut -d ':' -f2`
echo "JENKINS_IMAGE_ID: ${JENKINS_IMAGE_ID}"
TIMESTAMP=`date +%s`
echo -e "TIMESTAMP: ${TIMESTAMP}\n"

# If there was a config.xml like below:
# config-file-to-import/5bbc9ce244658c2a85a4d40f6caa3989f56dbfa9cc6d205b06b9e32e9ce172d0/1618493339/sample-export-config-file-20210415/config.xml
# remove directory from timestamp part, and just keep following directory:
# config-file-to-import/5bbc9ce244658c2a85a4d40f6caa3989f56dbfa9cc6d205b06b9e32e9ce172d0
rm -fR ${IMPORT_BASE_DIRECTORY}/${JENKINS_IMAGE_ID}/*

# Then create new directory like below with current timestamp:
# config-file-to-import/5bbc9ce244658c2a85a4d40f6caa3989f56dbfa9cc6d205b06b9e32e9ce172d0/1618546531
# 
#   1618493339: 2021-04-15 13:28:59
#   1618546531: 2021-04-16 04:15:31
# 
# "5bbc9ce24465..." part can change if Docker image of Jenkins is different.
# This logic assures only one config file set per Docker image of Jenkins, and timestamp allows us to identify the latest one.
mkdir -p ${IMPORT_BASE_DIRECTORY}/${JENKINS_IMAGE_ID}/${TIMESTAMP}

# Copy config.xml under EXPORTED_BASE_DIRECTORY, directory (/root/export) exposed from Jenkins container to IMPORT_BASE_DIRECTORY on host server..
for x in `find ${EXPORTED_BASE_DIRECTORY} -name config.xml`
do
  CONFIG_FILE=${x}
  echo "CONFIG_FILE: ${CONFIG_FILE}"
  JOB_NAME=`echo ${CONFIG_FILE} | cut -d '/' -f2`
  mkdir -p ${IMPORT_BASE_DIRECTORY}/${JENKINS_IMAGE_ID}/${TIMESTAMP}/${JOB_NAME}
  cp ${CONFIG_FILE} ${IMPORT_BASE_DIRECTORY}/${JENKINS_IMAGE_ID}/${TIMESTAMP}/${JOB_NAME}/
done
