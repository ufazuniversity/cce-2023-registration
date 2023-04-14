from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class StaticRootS3Boto3Storage(S3Boto3Storage):
    location = settings.AWS_STATIC_LOCATION


class MediaRootS3Boto3Storage(S3Boto3Storage):
    location = settings.AWS_MEDIA_LOCATION
    file_overwrite = False
