import boto3
import datetime
import psycopg2
import time

from fluent import sender
from fluent import event

unixtime = int(time.time())
print(unixtime)

ec2 = boto3.client('ec2')
responce = ec2.describe_instances()

for reservation in responce['Reservations']:
    for instance in reservation['Instances']:
        instance_id = instance['InstanceId']
        print(instance_id)

        body_dict = dict()
        body_dict['id'] = instance_id

        sender.setup(
                'awssql',
                host = 'localhost',
                port=8888)
        event.Event(
                'ec2',
                body_dict)
