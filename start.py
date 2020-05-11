#!/usr/bin/python3
import boto3
region = 'ap-south-1'
instances = ['i-05c70118a881cd854', 'i-04d753c4a5d3e66f2']
ec2 = boto3.client('ec2', region_name=region)
ec2.start_instances(InstanceIds=instances)
print('started your instances: ' + str(instances))

