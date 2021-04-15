#!/bin/bash
JENKINS_USER="root"
JENKINS_PASSWORD="root"
JENKINS_URL="localhost"
JENKINS_PORT="8080"

CSRF_CRUMB_COMMAND="curl --silent --cookie-jar /tmp/cookies -u '${JENKINS_USER}:${JENKINS_PASSWORD}' 'http://${JENKINS_URL}:${JENKINS_PORT}/crumbIssuer/api/xml?xpath=concat(//crumbRequestField,\":\",//crumb)'"
CSRF_CRUMB=`eval ${CSRF_CRUMB_COMMAND}`
echo "CSRF_CRUMB: ${CSRF_CRUMB}"

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

INDEX=1
for job_name in `eval ${JOBS_LIST_COMMAND}`
do
  JOB_NAME=${job_name}
  INDEX_ZERO_PAD=$(printf "%02d" "${INDEX}")
  echo "${INDEX_ZERO_PAD}: ${JOB_NAME}"
  mkdir -p ${EXPORT_BASE_DIRECTORY}/${JOB_NAME}
  curl -so ${EXPORT_BASE_DIRECTORY}/${JOB_NAME}/config.xml --user '${JENKINS_USER}:${JENKINS_PASSWORD}' http://${JENKINS_URL}:${JENKINS_PORT}/job/${JOB_NAME}/config.xml
  echo "    Exported config file to ${EXPORT_BASE_DIRECTORY}/${JOB_NAME}/config.xml"

  INDEX=$((${INDEX} + 1))
done
