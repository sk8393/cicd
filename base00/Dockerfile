FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive

COPY base00/init.sh /usr/local/bin/init.sh
COPY base00/td-agent.conf /tmp/td-agent.conf
COPY .ssh/id_rsa /tmp/id_rsa
COPY .ssh/id_rsa.pub /tmp/id_rsa.pub

RUN apt update
RUN apt install -y --no-install-recommends curl
RUN apt install -y --no-install-recommends gcc
RUN apt install -y --no-install-recommends git
RUN apt install -y --no-install-recommends gnupg
RUN apt install -y --no-install-recommends iproute2
RUN apt install -y --no-install-recommends iputils-ping
RUN apt install -y --no-install-recommends language-pack-en
RUN apt install -y --no-install-recommends less
RUN apt install -y --no-install-recommends libbz2-dev
RUN apt install -y --no-install-recommends libpq-dev
RUN apt install -y --no-install-recommends libreadline-dev
RUN apt install -y --no-install-recommends libsqlite3-dev
RUN apt install -y --no-install-recommends libssl-dev
RUN apt install -y --no-install-recommends make
RUN apt install -y --no-install-recommends openssh-server \
 && mkdir ~/.ssh \
 && cp /tmp/id_rsa ~/.ssh/id_rsa \
 && cp /tmp/id_rsa.pub ~/.ssh/authorized_keys \
 && chmod 0600 ~/.ssh/authorized_keys \
 && chmod 0600 ~/.ssh/id_rsa
RUN apt install -y --no-install-recommends sudo
RUN apt install -y --no-install-recommends unzip
RUN apt install -y --no-install-recommends vim
RUN apt install -y --no-install-recommends python3.8 \
 && ln -s /usr/bin/python3.8 /usr/bin/python3 \
 && ln -s /usr/bin/python3 /usr/bin/python
RUN apt install -y --no-install-recommends python3-pip \
 && ln -s /usr/bin/pip3 /usr/bin/pip
RUN apt install -y --no-install-recommends python3-setuptools
RUN apt install -y --no-install-recommends python3-dev
RUN pip install boto3
RUN curl -L "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
 && unzip awscliv2.zip \
 && ./aws/install \
 && rm awscliv2.zip \
 && mkdir ~/.aws
RUN pip install fluent-logger
RUN pip install psycopg2
RUN curl -L "https://github.com/tomnomnom/gron/releases/download/v0.6.1/gron-linux-amd64-0.6.1.tgz" -o "gron-linux-amd64-0.6.1.tgz" \
 && tar xzf gron-linux-amd64-0.6.1.tgz \
 && mv gron /usr/local/bin/ \
 && rm gron-linux-amd64-0.6.1.tgz
RUN apt install -y --no-install-recommends postgresql-10 \
 && echo "listen_addresses = '*'" >> /etc/postgresql/10/main/postgresql.conf \
 && echo "host all all 0.0.0.0/0 trust" >> /etc/postgresql/10/main/pg_hba.conf
RUN curl -L https://toolbelt.treasuredata.com/sh/install-ubuntu-bionic-td-agent3.sh | sh \
 && mv /etc/td-agent/td-agent.conf /etc/td-agent/td-agent.conf.bk \
 && mv /tmp/td-agent.conf /etc/td-agent/
RUN curl -L https://github.com/stedolan/jq/releases/download/jq-1.5/jq-linux64 -o /usr/local/bin/jq \
 && chmod +x /usr/local/bin/jq
RUN apt install -y --no-install-recommends nodejs
RUN apt install -y --no-install-recommends npm
RUN git clone https://github.com/c9/core.git cloud9 \
 && cd cloud9;./scripts/install-sdk.sh
RUN rm /usr/bin/python \
 && rm /usr/bin/python3 \
 && ln -s /usr/bin/python3.8 /usr/bin/python3 \
 && ln -s /usr/bin/python3 /usr/bin/python \
 && rm /usr/bin/pip \
 && ln -s /usr/bin/pip3 /usr/bin/pip
RUN pip install boto3
RUN pip install fluent-logger
RUN pip install psycopg2-binary
RUN rm -rf /var/lib/apt/lists/*
RUN chmod u+x /usr/local/bin/init.sh

CMD ["/usr/local/bin/init.sh"]
