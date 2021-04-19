#!/bin/bash
if [[ ${VARIABLES_LOADED} != "1" ]]
then
  source ../variables.sh
fi

curl -sSL "http://${JENKINS_USER}:${JENKINS_PASSWORD}@${JENKINS_URL}:${JENKINS_PORT}/pluginManager/api/xml?depth=1&xpath=/*/*/shortName|/*/*/version&wrapper=plugins" | perl -pe 's/.*?<shortName>([\w-]+).*?<version>([^<]+)()(<\/\w+>)+/\1 \2\n/g'|sed 's/ /:/' > ${JENKINS_BASE_DIRECTORY}/plugins.txt
