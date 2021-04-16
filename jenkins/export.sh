#!/bin/bash
JENKINS_USER="root"
JENKINS_PASSWORD="root"
JENKINS_URL="localhost"
JENKINS_PORT="8080"

# Crumb is used to diminish CSRF attacks using a random unique token that is created on the server side, Jenkins in this case.
# The token will be used for the next API call, retrieving list of jobs in this case.
# The token can not be re-used, so new crumb token has to be issued every time when API which requires crumb will be called.
CSRF_CRUMB_COMMAND="curl --silent --cookie-jar /tmp/cookies -u '${JENKINS_USER}:${JENKINS_PASSWORD}' 'http://${JENKINS_URL}:${JENKINS_PORT}/crumbIssuer/api/xml?xpath=concat(//crumbRequestField,\":\",//crumb)'"
CSRF_CRUMB=`eval ${CSRF_CRUMB_COMMAND}`
echo "CSRF_CRUMB: ${CSRF_CRUMB}"

# Retrieve list of jobs with following API call.
# JSON processor 'jq' has to be installed on Jenkins server beforehand.
JOBS_LIST_COMMAND="curl --cookie /tmp/cookies --user '${JENKINS_USER}:${JENKINS_PASSWORD}' -s -XPOST 'http://${JENKINS_URL}:${JENKINS_PORT}/api/json?tree=jobs[name]' -H "${CSRF_CRUMB}" | jq -r '.jobs[].name'"
echo "JOBS_LIST_COMMAND: ${JOBS_LIST_COMMAND}"
echo ""

# Remove just old config.xml and remain directory of job name.
# Sweeping entire directory can be dangerous like deleting import script file.
EXPORT_BASE_DIRECTORY="/root/export"
for old_config_file in `find ${EXPORT_BASE_DIRECTORY} -name config.xml`
do
  rm ${old_config_file}
  echo "Removed ${old_config_file}"
done
echo ""

# As of 2021-04-16, config file will be exported like /root/export/sample-end-to-end-pipeline-20210414/config.xml .
# Directory /root/export of container is mounted to host, so logic on host side can copy config file after Jenkins container stopped.
INDEX=1
for job_name in `eval ${JOBS_LIST_COMMAND}`
do
  JOB_NAME=${job_name}
  INDEX_ZERO_PAD=$(printf "%02d" "${INDEX}")
  echo "${INDEX_ZERO_PAD}: ${JOB_NAME}"
  mkdir -p ${EXPORT_BASE_DIRECTORY}/${JOB_NAME}
  EXPORT_COMMAND="curl -so ${EXPORT_BASE_DIRECTORY}/${JOB_NAME}/config.xml --user '${JENKINS_USER}:${JENKINS_PASSWORD}' http://${JENKINS_URL}:${JENKINS_PORT}/job/${JOB_NAME}/config.xml"
  echo "    EXPORT_COMMAND: ${EXPORT_COMMAND}"
  eval ${EXPORT_COMMAND}
  echo "    Exported config file to ${EXPORT_BASE_DIRECTORY}/${JOB_NAME}/config.xml"

  INDEX=$((${INDEX} + 1))
done
