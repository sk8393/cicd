#!/bin/bash
if [[ ${VARIABLES_LOADED} != "1" ]]
then
  source ../variables.sh
fi

LATEST_TIMESTAMP=`find ${JENKINS_IMPORT_BASE_DIRECTORY} -name config.xml | rev | cut -d '/' -f3 | rev | sort -n -r | head -n 1`
echo "$(printf "%${MAX_VARIABLE_LENGTH}s" "LATEST_TIMESTAMP"): ${LATEST_TIMESTAMP}"

IMPORT_SCRIPT=${JENKINS_BASE_DIRECTORY}/import.sh
echo "#!/bin/bash" > ${IMPORT_SCRIPT}

INDEX=0
for x in `find ${JENKINS_IMPORT_BASE_DIRECTORY} -name config.xml | grep ${LATEST_TIMESTAMP}`
do
  CONFIG_FILE_TO_IMPORT=${x}
  echo "$(printf "%${MAX_VARIABLE_LENGTH}s" "CONFIG_FILE_TO_IMPORT[${INDEX}]"): ${CONFIG_FILE_TO_IMPORT}"
  JOB_NAME=`echo ${CONFIG_FILE_TO_IMPORT} | rev | cut -d '/' -f2 | rev`
  echo "$(printf "%${MAX_VARIABLE_LENGTH}s" "JOB_NAME[${INDEX}]"): ${JOB_NAME}"

  CSRF_CRUMB='CSRF_CRUMB=$('
  CSRF_CRUMB+="curl --silent --cookie-jar /tmp/cookies -u '${JENKINS_USER}:${JENKINS_PASSWORD}' 'http://${JENKINS_URL}:${JENKINS_PORT}/crumbIssuer/api/xml?xpath=concat(//crumbRequestField,\":\",//crumb)'"
  CSRF_CRUMB+=')'
  echo "$(printf "%${MAX_VARIABLE_LENGTH}s" "CSRF_CRUMB[${INDEX}]"): ${CSRF_CRUMB}"
  echo ${CSRF_CRUMB} >> ${IMPORT_SCRIPT}

  IMPORT_COMMAND="curl --cookie /tmp/cookies --user '${JENKINS_USER}:${JENKINS_PASSWORD}' -s -XPOST http://${JENKINS_URL}:${JENKINS_PORT}/createItem?name=${JOB_NAME} --data-binary @${CONFIG_FILE_TO_IMPORT} -H 'Content-Type:text/xml' -H "\${CSRF_CRUMB}""
  echo "$(printf "%${MAX_VARIABLE_LENGTH}s" "IMPORT_COMMAND[${INDEX}]"): ${IMPORT_COMMAND}"
  echo "${IMPORT_COMMAND}" >> ${IMPORT_SCRIPT}

  INDEX=$((${INDEX} + 1))
done

chmod 774 ${IMPORT_SCRIPT}
echo "$(printf "%${MAX_VARIABLE_LENGTH}s" "MESSAGE"): "Run ${IMPORT_SCRIPT} to actually import jobs.""
