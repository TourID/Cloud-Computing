import pickle
import tensorflow as tf
from config.config import Config
from flask import Flask, request, jsonify
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model

# Load the trained model from Google Cloud Storage or local path
def load_model_locally():
    model = load_model(Config.MODEL_PATH, custom_objects={'mse': tf.keras.losses.MeanSquaredError()})
    return model

# Function to load user and place encodings
def load_encodings(path):
    with open(path, 'rb') as file:
        return pickle.load(file)

model = load_model_locally()
user_to_user_encoded = load_encodings(Config.USER_ENCODING_PATH)
place_to_place_encoded = load_encodings(Config.PLACE_ENCODING_PATH)

app = Flask(__name__)

# model = tf.keras.models.load_model(Config.MODEL_PATH, custom_objects={'mse': tf.keras.losses.MeanSquaredError()})

@app.route('/recommend', methods=['POST'])
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

if __name__ == '__main__':
    app.run(debug=True)