from storages.backends.s3boto3 import S3Boto3Storage


class S3Boto3StoragePublic(S3Boto3Storage):
    default_acl = 'public-read'
    file_overwrite = True


class PrivateMediaStorage(S3Boto3Storage):
    default_acl = 'private'
    file_overwrite = True
