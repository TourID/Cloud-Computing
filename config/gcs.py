from google.cloud import storage
from config.config import Config
from datetime import timedelta

def generate_signed_url(blob_name, expiration=timedelta(hours=1)):
    config_instance = Config()  # Create an instance of Config
    bucket_name = config_instance.BUCKET_NAME  # Get bucket name from Config instance
    credentials = config_instance.get_bucket_credentials()  # Call instance method
    client = storage.Client.from_service_account_json(credentials)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    url = blob.generate_signed_url(expiration=expiration)
    return url
