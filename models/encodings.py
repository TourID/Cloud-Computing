import joblib
from config.config import Config

user_to_user_encoded = joblib.load(Config.USER_ENCODING_PATH)
place_to_place_encoded = joblib.load(Config.PLACE_ENCODING_PATH)
