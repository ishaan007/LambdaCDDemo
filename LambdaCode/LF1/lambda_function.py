import json
import boto3
import re
import requests
from requests_aws4auth import AWS4Auth

import datetime

region = 'us-east-1'  # e.g. us-west-1
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)


# TODO: update
host = 'https://vpc-photos-cd-v3m6vhbcqpleevatzh2smo4wlm.us-east-1.es.amazonaws.com'  # the Amazon ES domain, including https://
index = 'photos-cd'
type = 'lambda-type'
url = host + '/' + index + '/' + type

headers = {"Content-Type": "application/json"}


# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# PDX-License-Identifier: MIT-0 (For details, see https://github.com/awsdocs/amazon-rekognition-developer-guide/blob/master/LICENSE-SAMPLECODE.)
def detect_labels(photo, bucket):
    client = boto3.client('rekognition')

    response = client.detect_labels(Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
                                    MaxLabels=12, MinConfidence=0.75)

    # print('Detected labels for ' + photo)
    labels = []
    for label in response['Labels']:
        labels.append(label['Name'])
        # print ("Label: " + label['Name'])
        # print ("Confidence: " + str(label['Confidence']))
    return labels


def lambda_handler(event, context):
    # print("EVENT:", event)
    # print("CONTEXT:", context)
    print("hello ow")
    bucket = event['Records'][0]['s3']['bucket']['name']
    img_key = event['Records'][0]['s3']['object']['key']
    # print(bucket)
    # print(img_key)

    # 1) Call Rekognition to get labels
    labels = detect_labels(img_key, bucket)

    # 2) Store JSON obbject in ElasticSearch
    timestamp = datetime.datetime.now()
    timestamp_str = timestamp.strftime("%Y-%m-%dT%H:%M:%S")

    document = {
        "objectKey": img_key,
        "bucket": bucket,
        "createdTimestamp": timestamp_str,
        "labels": labels
    }

    r = requests.post(url, auth=awsauth, json=document, headers=headers)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
