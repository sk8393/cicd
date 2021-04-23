FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive

COPY base00/init.sh /usr/local/bin/init.sh
COPY base00/td-agent.conf /tmp/td-agent.conf
COPY .aws/config /tmp/config
COPY .aws/credentials /tmp/credentials
COPY .ssh/id_rsa /tmp/id_rsa
COPY .ssh/id_rsa.pub /tmp/id_rsa.pub

RUN apt update \
 && apt install -y --no-install-recommends curl \
 && apt install -y --no-install-recommends gcc \
 && apt install -y --no-install-recommends git \
 && apt install -y --no-install-recommends gnupg \
 && apt install -y --no-install-recommends iproute2 \
 && apt install -y --no-install-recommends iputils-ping \
 && apt install -y --no-install-recommends less \
 && apt install -y --no-install-recommends libbz2-dev \
 && apt install -y --no-install-recommends libpq-dev \
 && apt install -y --no-install-recommends libreadline-dev \
 && apt install -y --no-install-recommends libsqlite3-dev \
 && apt install -y --no-install-recommends libssl-dev \
 && apt install -y --no-install-recommends make \
 && apt install -y --no-install-recommends openssh-server \
 && mkdir ~/.ssh \
 && cp /tmp/id_rsa ~/.ssh/id_rsa \
 && cp /tmp/id_rsa.pub ~/.ssh/authorized_keys \
 && chmod 0600 ~/.ssh/authorized_keys \
 && chmod 0600 ~/.ssh/id_rsa \
 && apt install -y --no-install-recommends sudo \
 && apt install -y --no-install-recommends unzip \
 && apt install -y --no-install-recommends vim \
 && apt install -y --no-install-recommends python3.8 \
 && ln -s /usr/bin/python3.8 /usr/bin/python3 \
 && ln -s /usr/bin/python3 /usr/bin/python \
 && apt install -y --no-install-recommends python3-pip \
 && ln -s /usr/bin/pip3 /usr/bin/pip \
 && apt install -y --no-install-recommends python3-setuptools \
 && apt install -y --no-install-recommends python3-dev \
 && pip install boto3 \
 && curl -L "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
 && unzip awscliv2.zip \
 && ./aws/install \
 && rm awscliv2.zip \
 && mkdir ~/.aws \
 && cp /tmp/config ~/.aws/config \
 && cp /tmp/credentials ~/.aws/credentials \
 && pip install fluent-logger \
 && pip install psycopg2 \
 && curl -L "https://github.com/tomnomnom/gron/releases/download/v0.6.1/gron-linux-amd64-0.6.1.tgz" -o "gron-linux-amd64-0.6.1.tgz" \
 && tar xzf gron-linux-amd64-0.6.1.tgz \
 && mv gron /usr/local/bin/ \
 && rm gron-linux-amd64-0.6.1.tgz \
 && apt install -y --no-install-recommends postgresql-10 \
 && echo "listen_addresses = '*'" >> /etc/postgresql/10/main/postgresql.conf \
 && echo "host all all 0.0.0.0/0 trust" >> /etc/postgresql/10/main/pg_hba.conf \
 && curl -L https://toolbelt.treasuredata.com/sh/install-ubuntu-bionic-td-agent3.sh | sh \
 && mv /etc/td-agent/td-agent.conf /etc/td-agent/td-agent.conf.bk \
 && mv /tmp/td-agent.conf /etc/td-agent/ \
 && rm -rf /var/lib/apt/lists/* \
 && chmod u+x /usr/local/bin/init.sh

CMD ["/usr/local/bin/init.sh"]
