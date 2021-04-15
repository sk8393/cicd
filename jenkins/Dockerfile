FROM jenkins/jenkins:2.287

USER root

COPY jenkins/plugins.txt /usr/share/jenkins/ref/plugins.txt

RUN /usr/local/bin/install-plugins.sh < /usr/share/jenkins/ref/plugins.txt \
 && apt update \
 && apt -y install vim \
 && rm -rf /var/lib/apt/lists/* \
 && curl -fL -o docker.tgz "https://download.docker.com/linux/static/test/x86_64/docker-19.03.4.tgz" \
 && tar --strip-components=1 -xvzf docker.tgz -C /usr/bin \
 && rm -f docker.tgz \
 && curl -L https://github.com/docker/compose/releases/download/1.16.1/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose \
 && chmod +x /usr/local/bin/docker-compose \
 && curl -L https://github.com/stedolan/jq/releases/download/jq-1.5/jq-linux64 -o /usr/local/bin/jq \
 && chmod +x /usr/local/bin/jq \
 && mkdir -p /root/export
