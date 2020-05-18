#!/usr/bin/python
import boto3
from boto3.session import Session
import collections
from datetime import datetime
from datetime import timedelta
import csv
from time import gmtime, strftime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
import os
from email import encoders


ACCOUNT_ID='377738922592'
#SES_SMTP_USER="AKIAVP4X6RJQMC6W3DVJ"
#SES_SMTP_PASSWORD="BML2MHXi/xZVtWrPtc1uGWkAc5dunNHM1cYVQ8uMjxzk"
MAIL_USER='awsmaintanance@gmail.com'
MAIL_PASSWORD='sgpl@admin'
MAIL_SUBJECT="Softility AWS Inventory for " + "softilitydevtest(377738922592) Account"
MAIL_BODY='Team,\nPFA., For Softility AWS Inventory of softilitydevtest(377738922592) Account.'
S3_INVENTORY_BUCKET="sftytraining"
#MAIL_FROM="testgeosol@gmail.com"
MAIL_TO=["hvadupu@softility.com",'sbathula@softility.com','hpommurapalli@softility.com','mgorukanti@softility.com']


#EC2 connection beginning
ec = boto3.client('ec2')
#S3 connection beginning
s3 = boto3.resource('s3')


 #get to the curren date
date_fmt = strftime("%Y_%m_%d %H:%M", gmtime())
    #Give your file path
filepath ='/tmp/SFTY_AWS_Resources_' + date_fmt + '.csv'
    #Give your filename
filename ='Softility_AWS_Resources_' + date_fmt + '.csv'
csv_file = open(filepath,'w+')

#IAM connection beginning - THIS Step should run only once not for every region:https://aws.amazon.com/iam/faqs/
iam = boto3.client('iam')
    #No region is needed since running it from lambda fixes it

    #boto3 library IAM API
    #http://boto3.readthedocs.io/en/latest/reference/services/iam.html
csv_file.write("%s,%s,%s,%s\n" % ('','','',''))
#csv_file.write("%s,%s\n"%('IAM',regname))
csv_file.write("%s"%('IAM'))
csv_file.write("%s,%s,%s,%s\n" % ('User','UserId','Policies','CreateDate'))
csv_file.flush()
users = iam.list_users()['Users']
for user in users:
    user_name = user['UserName']
    CreateDate = user['CreateDate']
    user_id = user['UserId']
    policies = ''
    user_policies = iam.list_user_policies(UserName=user_name)["PolicyNames"]
    for user_policy in user_policies:
        if(len(policies) > 0):
            policies += ";"
        policies += user_policy
    attached_user_policies = iam.list_attached_user_policies(UserName=user_name)["AttachedPolicies"]
    for attached_user_policy in attached_user_policies:
        if(len(policies) > 0):
            policies += ";"
        policies += attached_user_policy['PolicyName']
        #In case you need to write this at the end of the CSV make sure to move the 2 lines from below before mail function
    csv_file.write("%s,%s,%s,%s\n" % (user_name,user_id,policies,CreateDate))
    csv_file.flush()
regions = ec.describe_regions().get('Regions',[] )
for region in regions:
    reg=region['RegionName']
    regname='REGION :' + reg
        #EC2 connection beginning
    ec2con = boto3.client('ec2',region_name=reg)
        #boto3 library ec2 API describe instance page
        #http://boto3.readthedocs.org/en/latest/reference/services/ec2.html#EC2.Client.describe_instances
    reservations = ec2con.describe_instances().get(
    'Reservations',[]
    )
    instances = sum(
        [
            [i for i in r['Instances']]
            for r in reservations
        ], [])
    instanceslist = len(instances)
    if instanceslist > 0:
        csv_file.write("%s,%s,%s,%s,%s,%s\n"%('','','','','',''))
        csv_file.write("%s,%s\n"%('EC2 INSTANCE',regname))
        csv_file.write("%s,%s,%s,%s,%s,%s,%s\n"%('InstanceID','Instance_State','InstanceName','Instance_Type','LaunchTime','Instance_Placement', 'SecurityGroupsStr'))
        csv_file.flush()

    for instance in instances:
        state=instance['State']['Name']
        Instancename = 'N/A'
        if 'Tags' in instance:
            for tags in instance['Tags']:
                key = tags['Key']
                if key == 'Name' :
                    Instancename=tags['Value']
        if state =='running':
            instanceid=instance['InstanceId']
            instancetype=instance['InstanceType']
            launchtime =instance['LaunchTime']
            Placement=instance['Placement']['AvailabilityZone']
            securityGroups = instance['SecurityGroups']
            securityGroupsStr = ''
            for idx, securityGroup in enumerate(securityGroups):
                if idx > 0:
                    securityGroupsStr += '; '
                securityGroupsStr += securityGroup['GroupName']
            csv_file.write("%s,%s,%s,%s,%s,%s,%s\n"% (instanceid,state,Instancename,instancetype,launchtime,Placement,securityGroupsStr))
            csv_file.flush()

    for instance in instances:
        state=instance['State']['Name']
        Instancename = 'N/A'
        if 'Tags' in instance:
            for tags in instance['Tags']:
                key = tags['Key']
                if key == 'Name' :
                    Instancename=tags['Value']
        if state =='stopped':
            instanceid=instance['InstanceId']
            instancetype=instance['InstanceType']
            launchtime =instance['LaunchTime']
            Placement=instance['Placement']['AvailabilityZone']
            csv_file.write("%s,%s,%s,%s,%s,%s\n"%(instanceid,state,Instancename,instancetype,launchtime,Placement))
            csv_file.flush()

    amis = ec2con.describe_images(Owners=[
        ACCOUNT_ID,
    ]).get('Images',[])
    imagelist = len(amis)
    if imagelist > 0:
        csv_file.write("%s,%s,%s,%s,%s\n"%('','','','',''))
        csv_file.write("%s,%s\n"%('AMI',regname))
        csv_file.write("%s,%s,%s,%s\n" % ('Name','AMI Id','State','CreationDate'))
        csv_file.flush()
    for ami in amis:
        Name=ami['Name']
        ImageId=ami['ImageId']
        #Platform=ami['PlatformDetails']
        State=ami['State']
        CreationDate=ami['CreationDate']
        csv_file.write("%s,%s,%s,%s\n" % (Name,ImageId,State,CreationDate))
        csv_file.flush()
	
    ec2volumes = ec2con.describe_volumes().get('Volumes',[])
    volumeslist = len(ec2volumes)
    if volumeslist > 0:
        csv_file.write("%s,%s,%s,%s,%s\n"%('','','','',''))
        csv_file.write("%s,%s\n"%('EBS Volume',regname))
        csv_file.write("%s,%s,%s,%s,%s,%s,%s\n" % ('VolumeId','VolumeSize(GiB)','VolumeType','SnapshotId','State','AvailabilityZone','CreateTime'))
        csv_file.flush()

    for volume in ec2volumes:
        VolumeId=volume['VolumeId']
        Size=volume['Size']
        SnapshotId=volume['SnapshotId']
        State=volume['State']
        AvailabilityZone=volume['AvailabilityZone']
        VolumeType=volume['VolumeType']
        CreationDate=volume['CreateTime']
        csv_file.write("%s,%s,%s,%s,%s,%s,%s\n" % (VolumeId,Size,VolumeType,SnapshotId,State,AvailabilityZone,CreationDate))
        csv_file.flush()

        #boto3 library ec2 API describe snapshots page
        #http://boto3.readthedocs.org/en/latest/reference/services/ec2.html#EC2.Client.describe_snapshots
    ec2snapshot = ec2con.describe_snapshots(OwnerIds=[
        ACCOUNT_ID,
    ],).get('Snapshots',[])
    ec2snapshotlist = len(ec2snapshot)
    if ec2snapshotlist > 0:
        csv_file.write("%s,%s,%s,%s\n" % ('','','',''))
        csv_file.write("%s,%s\n"%('EC2 SNAPSHOT',regname))
        csv_file.write("%s,%s,%s,%s\n" % ('SnapshotId','VolumeId','StartTime','VolumeSize(GiB)'))
        csv_file.flush()

    for snapshots in ec2snapshot:
        SnapshotId=snapshots['SnapshotId']
        VolumeId=snapshots['VolumeId']
        StartTime=snapshots['StartTime']
        VolumeSize=snapshots['VolumeSize']
        csv_file.write("%s,%s,%s,%s\n" % (SnapshotId,VolumeId,StartTime,VolumeSize))
        csv_file.flush()

    addresses = ec2con.describe_addresses().get('Addresses',[] )
    addresseslist = len(addresses)
    if addresseslist > 0:
        csv_file.write("%s,%s,%s,%s,%s\n"%('','','','',''))
        csv_file.write("%s,%s\n"%('EIPS INSTANCE',regname))
        csv_file.write("%s,%s,%s\n"%('PublicIp','AllocationId','Domain'))
        csv_file.flush() 
        for address in addresses:
            PublicIp=address['PublicIp']
            AllocationId=address['AllocationId']
            Domain=address['Domain']
            csv_file.write("%s,%s,%s\n"%(PublicIp,AllocationId,Domain))
            csv_file.flush() 

    natgateways = ec2con.describe_nat_gateways().get('NatGateways',[])
    natgatewaylist = len(natgateways)
    if natgatewaylist > 0:
        csv_file.write("%s,%s,%s,%s\n"%('','','',''))
        csv_file.write("%s,%s\n"%('NatGateway',regname))
        csv_file.write("%s,%s,%s,%s\n"%('NatGatewayId','VpcId','State','CreateTime'))
        csv_file.flush()
    for gateway in natgateways:
        NatGatewayId=gateway['NatGatewayId']
        VpcId=gateway['VpcId']
        State=gateway['State']
        CreateTime=gateway['CreateTime']
        csv_file.write("%s,%s,%s,%s\n"%(NatGatewayId,VpcId,State,CreateTime))
        csv_file.flush()

    vpnconnections = ec2con.describe_vpn_connections().get('VpnConnections',[])
    vpnlist = len(vpnconnections)
    if vpnlist > 0:
        csv_file.write("%s,%s,%s,%s,%s\n"%('','','','',''))
        csv_file.write("%s,%s\n"%('VPN Connection',regname))
        csv_file.write("%s,%s,%s,%s,%s\n"%('VpnConnectionId','VpnGatewayId','CustomerGatewayId','Type','State'))
        csv_file.flush()
    for vpn in vpnconnections:
        VpnConnectionId=vpn['VpnConnectionId']
        VpnGatewayId=vpn['VpnGatewayId']
        CustomerGatewayId=vpn['CustomerGatewayId']
        Type=vpn['Type']
        State=vpn['State']
        csv_file.write("%s,%s,%s,%s,%s\n"%(VpnConnectionId,VpnGatewayId,CustomerGatewayId,Type,State))
        csv_file.flush()


    rdscon = boto3.client('rds',region_name=reg)

        #boto3 library RDS API describe db instances page
        #http://boto3.readthedocs.org/en/latest/reference/services/rds.html#RDS.Client.describe_db_instances
    rdb = rdscon.describe_db_instances().get(
    'DBInstances',[]
    )
    rdblist = len(rdb)
    if rdblist > 0:
        csv_file.write("%s,%s,%s,%s\n" %('','','',''))
        csv_file.write("%s,%s\n"%('RDS INSTANCE',regname))
        csv_file.write("%s,%s,%s,%s\n" %('DBInstanceIdentifier','DBInstanceStatus','DBName','DBInstanceClass'))
        csv_file.flush()

    for dbinstance in rdb:
        DBInstanceIdentifier = dbinstance['DBInstanceIdentifier']
        DBInstanceClass = dbinstance['DBInstanceClass']
        DBInstanceStatus = dbinstance['DBInstanceStatus']
        try:
            DBName = dbinstance['DBName']
        except:
            DBName = "empty"
        csv_file.write("%s,%s,%s,%s\n" %(DBInstanceIdentifier,DBInstanceStatus,DBName,DBInstanceClass))
        csv_file.flush()



        #ELB connection beginning
    elbcon = boto3.client('elb',region_name=reg)

        #boto3 library ELB API describe db instances page
        #http://boto3.readthedocs.org/en/latest/reference/services/elb.html#ElasticLoadBalancing.Client.describe_load_balancers
    loadbalancer = elbcon.describe_load_balancers().get('LoadBalancerDescriptions',[])
    loadbalancerlist = len(loadbalancer)
    if loadbalancerlist > 0:
        csv_file.write("%s,%s,%s,%s\n" % ('','','',''))
        csv_file.write("%s,%s\n"%('ELB INSTANCE',regname))
        csv_file.write("%s,%s,%s,%s\n" % ('LoadBalancerName','DNSName','CanonicalHostedZoneName','CanonicalHostedZoneNameID'))
        csv_file.flush()

    for load in loadbalancer:
        LoadBalancerName=load['LoadBalancerName']
        DNSName=load['DNSName']
        CanonicalHostedZoneName=load['CanonicalHostedZoneName']
        CanonicalHostedZoneNameID=load['CanonicalHostedZoneNameID']
        csv_file.write("%s,%s,%s,%s\n" % (LoadBalancerName,DNSName,CanonicalHostedZoneName,CanonicalHostedZoneNameID))
        csv_file.flush()




    lambdaclient = boto3.client('lambda',region_name=reg)
    lambdas = lambdaclient.list_functions().get('Functions',[])
    lambdalist = len(lambdas)
    if lambdalist > 0:
        csv_file.write("%s,%s,\n"%('',''))
        csv_file.write("%s,%s\n"%('Lambda',regname))
        csv_file.write("%s,%s\n"%('Function Name','Run Time'))
        csv_file.flush()
    for function in lambdas:
        functionname = function['FunctionName']
        RunTime = function['Runtime']
        csv_file.write("%s,%s\n"%(functionname,RunTime))
        csv_file.flush()
 
    


s3client = boto3.client('s3')
buckets = s3client.list_buckets()
s3list = len(buckets)
if s3list > 0:
    csv_file.write("%s,%s,\n"%('',''))
    csv_file.write("%s\n"%('S3 Buckets'))
    csv_file.write("%s,%s\n"%('Name','CreationDate'))
    csv_file.flush()

for bucket in buckets['Buckets']:
    Name = bucket['Name']
    CreationDate = bucket['CreationDate']
    csv_file.write("%s,%s\n"%(Name,CreationDate))
    csv_file.flush()



def printSecGroup(groupType, permission):
    ipProtocol = permission['IpProtocol']
    try:
        fromPort = permission['FromPort']
    except KeyError:
        fromPort = None
    try:
        toPort = permission['ToPort']
    except KeyError:
        toPort = None
    try:
        ipRanges = permission['IpRanges']
    except KeyError:
        ipRanges = []
    ipRangesStr = ''
    for idx, ipRange in enumerate(ipRanges):
        if idx > 0:
            ipRangesStr += '; '
        ipRangesStr += ipRange['CidrIp']
    csv_file.write("%s,%s,%s,%s,%s,%s,%s\n"%(groupName,groupId,groupType,ipProtocol,fromPort,toPort,ipRangesStr))
    csv_file.flush()
ec2sg = boto3.client('ec2', region_name = 'us-east-1')
securityGroups = ec2sg.describe_security_groups(
    Filters = [
        {
            'Name': 'owner-id',
            'Values': [
                ACCOUNT_ID,
            ]
        }
    ]
).get('SecurityGroups')
if len(securityGroups) > 0:
    csv_file.write("%s,%s,%s,%s,%s,%s\n"%('','','','','',''))
    csv_file.write("%s,%s\n"%('SEC GROUPS','us-east-1'))
    csv_file.write("%s,%s,%s,%s,%s,%s,%s\n"%('GroupName','GroupId','GroupType','IpProtocol','FromPort','ToPort','IpRangesStr'))
    csv_file.flush()
    for securityGroup in securityGroups:
        groupName = securityGroup['GroupName']
        groupId = securityGroup['GroupId']
        ipPermissions = securityGroup['IpPermissions']
        for ipPermission in ipPermissions:
            groupType = 'ingress'
            printSecGroup (groupType, ipPermission)
        ipPermissionsEgress = securityGroup['IpPermissionsEgress']
        for ipPermissionEgress in ipPermissionsEgress:
            groupType = 'egress'
            printSecGroup (groupType, ipPermissionEgress)



#ses_user = "AKIAVP4X6RJQMC6W3DVJ"
#ses_pwd = "BML2MHXi/xZVtWrPtc1uGWkAc5dunNHM1cYVQ8uMjxzk"

def mail(fromadd,to, subject, text, attach):
    msg = MIMEMultipart()
   # msg['From'] = fromadd
    msg['To'] = ','.join(MAIL_TO)
    msg['From'] = MAIL_USER
    #msg['To'] = MAIL_TO
    msg['Subject'] = subject
    msg.attach(MIMEText(text))
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(open(attach, 'rb').read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition','attachment; filename="%s"' % os.path.basename(attach))
    msg.attach(part)
   # mailServer = smtplib.SMTP("email-smtp.us-east-1.amazonaws.com", 587)
    mailServer = smtplib.SMTP('smtp.gmail.com',587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
   # mailServer.login(SES_SMTP_USER, SES_SMTP_PASSWORD)
    mailServer.login(MAIL_USER,MAIL_PASSWORD)
    mailServer.sendmail(fromadd, to, msg.as_string())
       # Should be mailServer.quit(), but that crashes...
    mailServer.close()

#date_fmt = strftime("%Y_%m_%d", gmtime())
    #Give your file path
#filepath ='/tmp/SFTY_AWS_Resources_' + date_fmt + '.csv'
    #Give your filename
mail(MAIL_USER, MAIL_TO, MAIL_SUBJECT, MAIL_BODY, filepath)
#mail("testgeosol@gmail.com","hvadupu@softility.com","SFTY AWS Resources","",filepath)
s3.Object(S3_INVENTORY_BUCKET,'AWSInventory/'+filename).put(Body=open(filepath, 'rb'))

