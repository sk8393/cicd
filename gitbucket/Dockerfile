FROM tomcat:8-jre8

ADD https://github.com/gitbucket/gitbucket/releases/download/4.14.1/gitbucket.war /opt/gitbucket.war

RUN ln -s /gitbucket /root/.gitbucket

EXPOSE 8080 29418

CMD ["java", "-jar", "/opt/gitbucket.war"]
