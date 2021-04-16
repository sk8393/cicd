#!/bin/bash
JENKINS_USER="root"
JENKINS_PASSWORD="root"
JENKINS_URL="localhost"
JENKINS_PORT="8889"

IMPORT_BASE_DIRECTORY="jenkins/config-file-to-import"
LATEST_TIMESTAMP=`find ${IMPORT_BASE_DIRECTORY} -maxdepth 3 -mindepth 3 | cut -d '/' -f4 | sort -n -r | head -n 1`
LATEST_TIMESTAMP_FORMATTED=`date -d @${LATEST_TIMESTAMP} +"%Y-%m-%d %T"`
LATEST_TIMESTAMP_DESCRIPTION="Last export happened at ${LATEST_TIMESTAMP_FORMATTED} (${LATEST_TIMESTAMP})"
echo ${LATEST_TIMESTAMP_DESCRIPTION}
echo ""

echo "#!/bin/bash" > import.sh

INDEX=1
for config_file in `find ${IMPORT_BASE_DIRECTORY} -name config.xml | grep ${LATEST_TIMESTAMP}`
do
  CONFIG_FILE_PATH=${config_file}
  echo "${INDEX}: ${CONFIG_FILE_PATH}"
  CONFIG_FILE_DIRECTORY=`find ${IMPORT_BASE_DIRECTORY} -name config.xml | grep ${LATEST_TIMESTAMP} | xargs dirname`
  JOB_NAME=`echo ${CONFIG_FILE_PATH} | cut -d '/' -f5`
  echo "   JOB_NAME: ${JOB_NAME}"

  # echo "curl --silent --cookie-jar /tmp/cookies -u '${JENKINS_USER}:${JENKINS_PASSWORD}' 'http://${JENKINS_URL}:${JENKINS_PORT}/crumbIssuer/api/xml?xpath=concat(//crumbRequestField,":",//crumb)'" >> import.sh
  CSRF_CRUMB='CSRF_CRUMB=$('
  CSRF_CRUMB+="curl --silent --cookie-jar /tmp/cookies -u '${JENKINS_USER}:${JENKINS_PASSWORD}' 'http://${JENKINS_URL}:${JENKINS_PORT}/crumbIssuer/api/xml?xpath=concat(//crumbRequestField,\":\",//crumb)'"
  CSRF_CRUMB+=')'
  echo ${CSRF_CRUMB} >> import.sh

  IMPORT_COMMAND="curl --cookie /tmp/cookies --user '${JENKINS_USER}:${JENKINS_PASSWORD}' -s -XPOST http://${JENKINS_URL}:${JENKINS_PORT}/createItem?name=${JOB_NAME} --data-binary @${CONFIG_FILE_PATH} -H 'Content-Type:text/xml' -H "\${CSRF_CRUMB}""
  echo "   IMPORT_COMMAND: ${IMPORT_COMMAND}"
  echo "${IMPORT_COMMAND}" >> import.sh
  echo ""

  INDEX=$((${INDEX} + 1))
done

chmod 774 import.sh
echo "Run import.sh to actually import jobs."
