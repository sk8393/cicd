FROM sk8393/base02:test

RUN echo "cd /root;git clone https://github.com/sk8393/cicd.git" >> /usr/local/bin/init.sh
RUN echo "node /cloud9/server.js -p 8080 -a root:root -w /root/ -l 0.0.0.0" >> /usr/local/bin/init.sh
