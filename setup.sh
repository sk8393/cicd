#!/bin/bash
if [[ ${VARIABLES_LOADED} != "1" ]]
then
  source ./variables.sh
fi

if [[ `whoami` = "root" ]]
then
  echo "$(printf "%${MAX_VARIABLE_LENGTH}s" "EXIT"): "Need to be non root user to avoid error in git command.""
  exit 1
fi

if [ ! -f ./.aws/credentials ]; then
  echo "$(printf "%${MAX_VARIABLE_LENGTH}s" "EXIT"): "Create .aws/credentials with AWS access key.""
  exit 1
fi

# Set up local branch that corresponds to existing remote branch.
./fetch.sh

# nano is the default editor on Ubuntu that I am not familiar with.
git config --global core.editor vim

sudo ./create_docker_image_gitbucket.sh

sudo ./create_docker_image_jenkins.sh

sudo ./create_docker_compose_project_cicd.sh

# # Launch Jenkins container and confirm initial password with command below.
# sudo docker ps -a | grep jenkins | cut -d " " -f1 | xargs sudo docker logs

# # Import past Jenkins job with exported config.xml.
# # Inbound rule of security group has to be opene for all traffic.
# cd jenkins;./create_import.sh.sh
# cd jenkins;./import.sh

# # Check volumes defined in jenkins/docker-compose.yml is OK.
