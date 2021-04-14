#!/bin/bash
curl -sSL "http://admin:7769a4f5b9e648e1a737d74322e90458@jenkins.sk8393.pw:8889/pluginManager/api/xml?depth=1&xpath=/*/*/shortName|/*/*/version&wrapper=plugins" | perl -pe 's/.*?<shortName>([\w-]+).*?<version>([^<]+)()(<\/\w+>)+/\1 \2\n/g'|sed 's/ /:/' > plugins.txt
