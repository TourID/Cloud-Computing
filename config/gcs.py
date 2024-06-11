from google.cloud import storage
from config import Config

def generate_signed_url(bucket_name, blob_name, expiration_time=900):
    client = storage.Client.from_service_account_json(Config.GOOGLE_APPLICATION_CREDENTIALS)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    url = blob.generate_signed_url(expiration=expiration_time)
    return url
