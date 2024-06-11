import os

class Config:
    BUCKET_NAME = 'tourid-bucket'
    GOOGLE_APPLICATION_CREDENTIALS = "config/firestore-config.json"
    PROJECT = 'capstone-tourid'
    DATABASE = 'tourid'
    MODEL_PATH = 'models/best_model.h5'
    USER_ENCODING_PATH = 'models/user_to_user_encoded.pkl'
    PLACE_ENCODING_PATH = 'models/place_to_place_encoded.pkl'
    PLACE_DATA_PATH = 'models/place_data.csv'
    GCS_CONFIG_PATH = "config/gcs.py"
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS
