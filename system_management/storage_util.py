# storage.py
import uuid
import boto3
import hashlib
import mimetypes
import pathlib
from django.conf import settings
from botocore.exceptions import ClientError

from botocore.config import Config


def get_backblaze_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.BACKBLAZE_ENDPOINT_URL,
        aws_access_key_id=settings.BACK_BLAZE_KEY_ID,
        aws_secret_access_key=settings.BACK_BLAZE_APLLICATION_KEY,
        config=Config(signature_version="s3v4"),
        region_name="us-east-005",  # REQUIRED
    )


def upload_document_to_backblaze(file, case_id, filename):
    """
    Upload a case document to Backblaze B2.
    Returns: (public_url, checksum, file_size) or (None, None, None) if failed
    """
    bucket = settings.BACK_BLAZE_BUCKET_NAME

    # Organize by case
    sanitized_name = pathlib.Path(filename).stem.replace(' ', '_').lower()
    extension = pathlib.Path(filename).suffix
    # key = f"documents/case_{case_id}/{sanitized_name}{extension}"
    key = f"documents/case_{case_id}/{uuid.uuid4()}_{sanitized_name}{extension}"

    content_type, _ = mimetypes.guess_type(filename)
    if not content_type:
        content_type = 'application/octet-stream'

    try:
        file.seek(0)
        file_content = file.read()
        checksum = hashlib.sha256(file_content).hexdigest()
        file_size = len(file_content)
        file.seek(0)

        s3 = get_backblaze_client()
        s3.upload_fileobj(
            file,
            bucket,
            key,
            ExtraArgs={
    'ContentType': content_type,
    'Metadata': {
        'case_id': str(case_id),
        'checksum': checksum,
    }
}
            # ExtraArgs={
            #     'ContentType': content_type,
            #     'ContentDisposition': f'inline; filename="{filename}"',
            #     'Metadata': {
            #         'case_id': str(case_id),
            #         'checksum': checksum,
            #     }
            # }
        )

        # url = f"{settings.BACKBLAZE_ENDPOINT_URL}/{bucket}/{key}"
        # return url, checksum, file_size
        return None, checksum, file_size, key

    except ClientError as e:
        print(f"[UPLOAD ERROR] {e}")
        return None, None, None


def get_presigned_url(file_path, expires_in=3600):
    """
    Generate a presigned URL for viewing/downloading a document.
    file_path: S3 key stored on the Document model
    """
    bucket = settings.BACK_BLAZE_BUCKET_NAME

    try:
        s3 = get_backblaze_client()
        url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': bucket,
                'Key': file_path,
                'ResponseContentDisposition': 'inline',
            },
            ExpiresIn=expires_in
        )
        return url

    except ClientError as e:
        print(f"[PRESIGN ERROR] {e}")
        return None


def delete_document_from_backblaze(file_path):
    """
    Delete a document from Backblaze B2.
    file_path: S3 key stored on the Document model
    Returns: True if successful, False otherwise
    """
    # bucket = settings.BACK_BLAZE_KEY_ID
    bucket = settings.BACK_BLAZE_BUCKET_NAME  # ✅

    try:
        s3 = get_backblaze_client()
        s3.delete_object(Bucket=bucket, Key=file_path)
        return True

    except ClientError as e:
        print(f"[DELETE ERROR] {e}")
        return False