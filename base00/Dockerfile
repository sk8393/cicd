FROM ubuntu:18.04

COPY base00/init.sh /usr/local/bin/init.sh
COPY .ssh/id_rsa /tmp/id_rsa
COPY .ssh/id_rsa.pub /tmp/id_rsa.pub

RUN apt-get -y update \
 && apt-get -y upgrade \
 && apt-get -y --no-install-recommends install openssh-server=1:7.6p1-4ubuntu0.3 \
 && rm -rf /var/lib/apt/lists/* \
 && mkdir ~/.ssh \
 && cp /tmp/id_rsa ~/.ssh/id_rsa \
 && cp /tmp/id_rsa.pub ~/.ssh/authorized_keys \
 && chmod 0600 ~/.ssh/authorized_keys \
 && chmod 0600 ~/.ssh/id_rsa \
 && chmod u+x /usr/local/bin/init.sh

CMD ["/usr/local/bin/init.sh"]
