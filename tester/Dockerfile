FROM sk8393/base02:test

COPY tester/test.sh /root/

RUN chmod u+x /root/test.sh \
 && echo "while :; do sleep 10; done" >> /usr/local/bin/init.sh
