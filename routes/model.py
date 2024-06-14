from flask import Blueprint, request, jsonify
import numpy as np
from models.encodings import user_to_user_encoded, place_to_place_encoded
import pickle
import tensorflow as tf
from config.config import Config
import pandas as pd

model_bp = Blueprint('model', __name__)

# Load the trained model from Google Cloud Storage or local path
def load_model_locally():
    model = tf.keras.models.load_model(Config.MODEL_PATH, custom_objects={'mse': tf.keras.losses.MeanSquaredError()})
    return model

# Function to load user and place encodings
def load_encodings(path):
    with open(path, 'rb') as file:
        return pickle.load(file)

model = load_model_locally()
user_to_user_encoded = load_encodings(Config.USER_ENCODING_PATH)
place_to_place_encoded = load_encodings(Config.PLACE_ENCODING_PATH)

@model_bp.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    num_users = data['num_users']
    num_places = data['num_places']

    # Create DataFrame with all possible user-place pairs
    all_users = np.array(list(user_to_user_encoded.values()))
    all_places = np.array(list(place_to_place_encoded.values()))
    all_user_place = np.array(np.meshgrid(all_users, all_places)).T.reshape(-1, 2)
    df_all_user_place = pd.DataFrame(all_user_place, columns=['user', 'place'])

    # Predict ratings
    predictions = model.predict([df_all_user_place['user'], df_all_user_place['place']])

    # Add predicted ratings to DataFrame
    df_all_user_place['predicted_rating'] = predictions.flatten()

    # Sort DataFrame by predicted rating
    df_recommendations = df_all_user_place.sort_values(by='predicted_rating', ascending=False)

    # Get top 10 recommendations
    top_recommendations = df_recommendations.head(10).to_dict(orient='records')

    return jsonify(top_recommendations)

# @predict_bp.route('/predict', methods=['POST'])
# def predict():
#     data = request.json
#     user_id = data.get('user_id')
#     place_id = data.get('place_id')

#     user_encoded = user_to_user_encoded.get(user_id, None)
#     place_encoded = place_to_place_encoded.get(place_id, None)

#     if user_encoded is None or place_encoded is None:
#         return jsonify({'error': 'User or Place not found'}), 400

#     user_input = np.array([user_encoded]).reshape(1, -1)
#     place_input = np.array([place_encoded]).reshape(1, -1)

#     prediction = model.predict([user_input, place_input])
#     rating = float(prediction[0][0])

#     return jsonify({'rating': rating})
