import boto3
import logging
import requests

from botocore.exceptions import ClientError

s3 = boto3.client('s3')

def handler(event, context):
    # Generate a presigned S3 POST URL
    s3_event = event['Records'][0]['s3']
    bucket_name = s3_event['bucket']['name']
    object_key = s3_event['object']['key']
    logger.info(f'Reading {object_key} from {bucket_name}')
    object_data = s3.get_object(Bucket=bucket_name, Key=object_key)
    print(object_data)
