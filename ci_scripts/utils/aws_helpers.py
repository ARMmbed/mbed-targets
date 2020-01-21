"""Helpers for interacting with AWS services such as S3.

Based on the Python SDK called BOTO https://aws.amazon.com/sdk-for-python/.
"""
import boto3
import logging
import os
import mimetypes

BUCKET = 'mbed-target'

logger = logging.getLogger(__name__)

S3_REGION = os.getenv('AWS_DEFAULT_REGION', 'eu-west-2')
S3_CONFIG = {
    "aws_access_key_id": os.getenv('AWS_ACCESS_KEY_ID'),
    "aws_secret_access_key": os.getenv('AWS_SECRET_ACCESS_KEY'),
}


def upload_file(file: str, bucket_dir: str):
    """Uploads a file onto AWS S3.

    Args:
        file: path to the file to upload
        bucket_dir: name of the folder where to put the file in S3 bucket
    """
    logger.info(f'Uploading {file} to AWS')
    if not file or not os.path.exists(file):
        raise FileNotFoundError(file)
    client = boto3.client('s3', **S3_CONFIG)
    dest_dir = (bucket_dir + '/' if bucket_dir else '')
    dest_filename = os.path.basename(file)
    key = f'{dest_dir}{dest_filename}'
    filename, extension = os.path.splitext(file)
    client.upload_file(
        file, BUCKET, key,
        ExtraArgs={
            'ContentType': mimetypes.types_map.get(extension,
                                                   'application/octet-stream')
        } if extension else {}
    )
    # Ensures the file is publicly available and reachable
    # by anyone having access to the bucket.
    client.put_object_acl(
        ACL='public-read',
        Bucket=BUCKET,
        Key=key
    )


def upload_directory(dir: str, bucket_dir: str):
    """Uploads the contents of a directory (recursively) onto AWS S3.

    Args:
        dir: folder to upload
        bucket_dir: name of the folder where to put the directory contents in S3 bucket
    """
    logger.info(f'Uploading {dir} to AWS')
    if not dir or not os.path.exists(dir):
        raise FileNotFoundError(dir) if dir else ValueError(dir)
    if os.path.isfile(dir):
        upload_file(dir, bucket_dir)
        return

    def onerror(exception):
        logger.error(exception)

    real_dir_path = os.path.realpath(dir)
    for root, dirs, files in os.walk(real_dir_path, followlinks=True,
                                     onerror=onerror):
        if root != real_dir_path:
            new_bucket_dir = os.path.join(
                bucket_dir, os.path.relpath(root, start=dir)
            )
        else:
            new_bucket_dir = bucket_dir
        new_bucket_dir = new_bucket_dir.replace(os.sep, '/')
        for name in files:
            upload_file(os.path.join(root, name), new_bucket_dir)
        for name in dirs:
            upload_directory(os.path.join(root, name), new_bucket_dir)
