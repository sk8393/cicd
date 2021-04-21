#!/bin/bash
sed -i".bk" -e "s/peer/trust/g" /etc/postgresql/10/main/pg_hba.conf

/etc/init.d/postgresql start

psql -U postgres -c "CREATE DATABASE ${DB_NAME};"
psql -U postgres -d ${DB_NAME} -c "CREATE ROLE ${DB_ROOT_USER} WITH LOGIN PASSWORD '${DB_ROOT_PASSWORD}' SUPERUSER;"
psql -U postgres -d ${DB_NAME} -c "REVOKE CONNECT ON DATABASE ${DB_NAME} FROM PUBLIC;"
psql -U postgres -d ${DB_NAME} -c "REVOKE ALL ON SCHEMA public FROM PUBLIC;"
psql -U postgres -d ${DB_NAME} -c "CREATE SCHEMA ${DB_ROOT_SCHEMA};"

psql -U postgres -d ${DB_NAME} -c \
"CREATE TABLE ${DB_ROOT_SCHEMA}.ec2_describe_instances_instances \
(_id VARCHAR(64) PRIMARY KEY, \
_timestamp INTEGER);"

psql -U postgres -d ${DB_NAME} -c \
"INSERT INTO ${DB_ROOT_SCHEMA}.ec2_describe_instances_instances VALUES ('i-xxxxxxxxxxxxxxxxx', 1618977323);"

/etc/init.d/postgresql stop

sudo -u postgres /usr/lib/postgresql/10/bin/postgres -D /var/lib/postgresql/10/main -c config_file=/etc/postgresql/10/main/postgresql.conf
