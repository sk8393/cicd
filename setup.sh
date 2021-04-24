# Set up local branch that corresponds to existing remote branch.
./fetch.sh

# nano is the default editor on Ubuntu that I am not familiar with.
git config --global core.editor vim

# Create .aws/credentials with AWS access key.

sudo ./create_docker_image_gitbucket.sh
sudo ./create_docker_image_jenkins.sh
sudo ./create_docker_compose_project_cicd.sh

sudo docker ps -a | grep jenkins | cut -d " " -f1 | xargs sudo docker logs

# Inbound rule of security group has to be opene for all traffic.
cd jenkins;./create_import.sh.sh
cd jenkins;./import.sh

# Check volumes defined in jenkins/docker-compose.yml is OK.
