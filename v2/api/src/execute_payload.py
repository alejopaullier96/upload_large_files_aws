import boto3
import numpy as np

from botocore.exceptions import ClientError
from io import BytesIO
from PIL import Image

s3 = boto3.client('s3')

def read_byte_image(byte_image):
    """
    Reads an image from bytes.
    :param byte_image: byte encoded image.
    """
    im = Image.open(byte_image)
    return np.array(im)


def write_image_to_s3(img_array, bucket_name, key, region='us-east-1'):
    """
    Write an image array into S3 bucket
    :param img_array: Image as numpy array.
    :param bucket_name: Bucket name
    :param key: object key/name.
    :param region_name: Bucket's region.
    :return: None.
    """
    s3 = boto3.resource('s3', region) 
    bucket = s3.Bucket(bucket_name)
    obj = bucket.Object(key)
    file_stream = BytesIO()
    im = Image.fromarray(img_array)
    im.save(file_stream, format='jpeg')
    obj.put(Body=file_stream.getvalue())


def handler(event, context):
    # Generate a presigned S3 POST URL
    s3_event = event['Records'][0]['s3']
    bucket_name = s3_event['bucket']['name']
    object_key = s3_event['object']['key']
    destination_bucket = "my-microservice-preprocessed-xxx" # HARDCODED
    print(f'Reading {object_key} from {bucket_name}')
    object_data = s3.get_object(Bucket=bucket_name, Key=object_key)
    byte_image = object_data["Body"] # byte encoded image
    metadata = object_data["Metadata"] # user metadata
    image = read_byte_image(byte_image) # get image as numpy array
    object_key = metadata["id"] + "/" + s3_event['object']['key'] # save the image under the user's folder
    write_image_to_s3(image, destination_bucket, object_key, region='us-east-1')
