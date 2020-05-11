import boto3
import paramiko
import time
import cmd
import sys


client = boto3.client('ec2', region_name='ap-south-1',aws_access_key_id="AKIAIPEGG7AOHJPHSJIQ",aws_secret_access_key="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")
########## Filter Instances With Specified Tags ############
response = client.describe_instances(
    Filters=[
        {
            'Name': 'tag:Name',
            'Values': [
                'TeamDE',
            ]
        }
    ]
)


for reservation in (response["Reservations"]):
    for instance in reservation["Instances"]:

####### REMOTE EC2 SERVER DEFAULTS #############
        Id = instance["InstanceId"]
        PrivateIP = instance["PrivateIpAddress"]
        PrivateDNS = instance["PrivateDnsName"]
        username = "ec2-user"
        key_filename = "/home/ec2-user/tes.pem"
        print(Id)
        print(PrivateIP)
        print(PrivateDNS)
        print(response)

########### SSH INTO SERVERS ###############
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privkey = paramiko.RSAKey.from_private_key_file('/home/ec2-user/test.pem')
        ssh.connect(instance["PrivateIpAddress"],username='ec2-user',key_filename='/home/ec2-user/test.pem') 

############ Add Bash Script file for server configuration ###########
        bash_script = open("script.sh").read()      
        # execute the BASH script
        stdin, stdout, stderr = ssh.exec_command(bash_script)

######### Read the standard output and print it #########
        print(stdout.read().decode())

######### print errors if there are any #########
        err = stderr.read().decode()
        if err:
            print(err)

############ close the connection ##############
        ssh.close()  
