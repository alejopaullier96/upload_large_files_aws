import boto3
import json
import logging
import uuid

from botocore.exceptions import ClientError

def handler(event, context):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """
    BUCKET_NAME = "my-very-large-bucket-api"
    OBJECT_NAME = str(uuid.uuid4())
    EXPIRATION = 60 * 5

    # Generate a presigned S3 POST URL
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': BUCKET_NAME,
                                                            'Key': OBJECT_NAME},
                                                    ExpiresIn=EXPIRATION)
    except ClientError as e:
        logging.error(e)
        return {
			"statusCode": 400,
			"headers": {
				"Access-Control-Allow-Origin": "*",
			},
			"body": e,
		}

    return {
			"statusCode": 200,
			"headers": {
				"Access-Control-Allow-Origin": "*",
			},
			"body": json.dumps({"url":response})
		}    
    