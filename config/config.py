from google.cloud import secretmanager

class Config:
    BUCKET_SECRET_NAME = "projects/capstone-tourid/secrets/bucket-secret/versions/latest"
    FIRESTORE_SECRET_NAME = "projects/capstone-tourid/secrets/firestore-secret/versions/latest"
    PROJECT = 'capstone-tourid'
    BUCKET_NAME = 'tourid-bucket'
    DATABASE = 'tourid'
    MODEL_PATH = 'models/best_model.h5'
    USER_ENCODING_PATH = 'models/user_to_user_encoded.pkl'
    PLACE_ENCODING_PATH = 'models/place_to_place_encoded.pkl'
    PLACE_DATA_PATH = 'models/place_data.csv'
    GCS_CONFIG_PATH = 'config/gcs.py'

    @staticmethod
    def get_secret(secret_name):
        client = secretmanager.SecretManagerServiceClient()
        response = client.access_secret_version(name=secret_name)
        return response.payload.data.decode('utf-8')

    def get_bucket_credentials(self):
        return self.get_secret(self.BUCKET_SECRET_NAME)

    def get_firestore_credentials(self):
        return self.get_secret(self.FIRESTORE_SECRET_NAME)