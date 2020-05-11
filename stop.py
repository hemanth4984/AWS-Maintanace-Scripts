#!/usr/bin/python3
import boto3
region = 'ap-south-1'
instances = ['i-********', 'i-***********']
ec2 = boto3.client('ec2', region_name=region)
ec2.stop_instances(InstanceIds=instances)
print('stopped your instances: ' + str(instances))
