import boto3
import json

ec2 = boto3.client('ec2')
def lambda_handler(event, context):
    print("hello world")
    print("hello world 2")
    print("adi yarne")
    response = ec2.describe_availability_zones()
    return {"statusCode": 200, "body": json.dumps(response)}
