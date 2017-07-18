import json
import datetime
import os
import time
import boto3
import logging

# logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# create boto clients
cloudwatch = boto3.client('cloudwatch')
ec2_r = boto3.resource('ec2')
ec2_c = boto3.client('ec2')

""" --- Functions that control the bot's behavior --- """

def instance_count(intent_request):
    num_volumes = sum(1 for _ in ec2_r.volumes.all())
    num_instances = sum(1 for _ in ec2_r.instances.all())

    calculated_count = {
        "dialogAction": {
          "type": "Close",
          "fulfillmentState": "Fulfilled",
          "message": {
            "contentType": "PlainText",
            "content": "You have " + str(num_instances) + " instances and "+ str(num_volumes) + " volumes."
          }
        }
    }
    
    return calculated_count

def launch_instance(intent_request):
    ami = intent_request['currentIntent']['slots']['AMI'].lower().replace(" ", "")
    type = intent_request['currentIntent']['slots']['TYPE'].lower().replace(" ", "")
    number = intent_request['currentIntent']['slots']['NUMBER'].lower().replace(" ", "")
    storage = intent_request['currentIntent']['slots']['STORAGE'].lower().replace(" ", "")

    ami_choices = {
        'ubuntu' : "ami-d15a75c7",
        'redhat': "ami-9e2f0988",
        'amazonlinux' : "ami-a4c7edb2",
        'windows' : "ami-f4d1f0e2"
    }
    
    type_choices = {
        't2micro': "t2.micro",
        't2small': "t2.small",
        't2medium': "t2.medium"
    }
    
    number_choices = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "1": 1,
        "2": 2,
        "3": 3,
        "4": 4,
        "5": 5
    }
    
    storage_choices = {
        'generalpurpose': "gp2",
        'provisioned': "io1",
        'magnetic': "standard",
    }
    
    if ami in ami_choices and type in type_choices and storage in storage_choices and number_choices[number] >= 1 and number_choices[number] < 5:
        ec2_r.create_instances(ImageId=ami_choices[ami], InstanceType=type_choices[type], MinCount=number_choices[number], MaxCount=number_choices[number], Placement={'AvailabilityZone': 'us-east-1b'}, BlockDeviceMappings=[{ 'DeviceName': "/dev/xvda", 'Ebs': { 'VolumeSize': 10, 'VolumeType': storage_choices[storage] } }], NetworkInterfaces=[{'DeviceIndex': 0, 'SubnetId': "subnet-62827c15"}])
        return {
            "dialogAction": {
            "type": "Close",
            "fulfillmentState": "Fulfilled",
                "message": {
                  "contentType": "PlainText",
                  "content": "Instance launched!"
                }
            }
        }
    else:
        return {
            "dialogAction": {
            "type": "Close",
            "fulfillmentState": "Failed",
                "message": {
                  "contentType": "PlainText",
                  "content": "The instance could not be launched! Check your parameter inputs -- AMI: " + ami_choices[ami] + ", instance type: " + type_choices[type] + ", number of instances: " + number + " storage type: " + storage_choices[storage]
                }
            }
        }
    
def instance_status(intent_request):
    running_instances = len(ec2_c.describe_instance_status(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])['InstanceStatuses'])
    stopped_instances = len(ec2_c.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['stopped'],}])["Reservations"])

    return {
        "dialogAction": {
          "type": "Close",
          "fulfillmentState": "Fulfilled",
          "message": {
            "contentType": "PlainText",
            "content": "There are " + str(running_instances) + " running instances and " + str(stopped_instances) + " stopped instances."
          }
        }
    }

# --- Intents ---

def dispatch(intent_request):
    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'Count':
        return instance_count(intent_request)
    elif intent_name == 'LaunchInstance':
        return launch_instance(intent_request)
    elif intent_name == 'Status':
        return instance_status(intent_request)
    else:
        return "Nothing found!"

    raise Exception('Intent with name ' + intent_name + ' not supported')

# --- Main handler ---

def lambda_handler(event, context):
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)

