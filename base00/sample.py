import boto3
import datetime
import psycopg2
import time

from fluent import sender
from fluent import event

time.sleep(30)

while 1:
    _timestamp = int(time.time())
    print(_timestamp)

    ec2 = boto3.client('ec2')
    responce = ec2.describe_instances()

    for reservation in responce['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            print(instance_id)
            _id = instance_id

            connection = psycopg2.connect("host={0} port={1} user={2} password={3} dbname={4}".format("postgres", "5432", "root", "acd483de", "awssql"))
            cursor = connection.cursor()
            cursor.execute('INSERT INTO root.ec2_describe_instances_instances (_id, _timestamp) VALUES (%s, %s);', (instance_id, _timestamp))
            connection.commit()

            body_dict = dict()
            body_dict['instance_id'] = instance_id
            body_dict['message'] = "test message to elasticsearch"

            sender.setup(
                    'awssql',
                    host = 'localhost',
                    port=8888)
            event.Event(
                    'rds',
                    body_dict)

    time.sleep(10)
