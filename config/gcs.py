from google.cloud import storage
from config.config import Config
from datetime import timedelta

def generate_signed_url(bucket_name, blob_name, expiration=timedelta(hours=1)):
    client = storage.Client.from_service_account_json(Config.BUCKET_CREDENTIALS)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    # Log for debugging
    # print(f"Generating signed URL for bucket: {bucket_name}, blob: {blob_name}")
    url = blob.generate_signed_url(expiration=expiration)
    return url
