from flask import Blueprint, request, jsonify
import numpy as np
import pickle
from tensorflow.keras.models import load_model
from tensorflow.keras.losses import MeanSquaredError
import pandas as pd
from config.config import Config
from routes.places import getPlace
from routes.users import get_all_users,get_uid_model
from routes.reviews import get_all_ratings,get_reviews,calculate_rating


model_bp = Blueprint('model', __name__)

# Load the trained model from Google Cloud Storage or local path
def load_model_locally():
    modell = load_model(Config.MODEL_PATH, custom_objects={'mse': MeanSquaredError()})
    return modell

# Function to load user and place encodings
def load_encodings(path):
    with open(path, 'rb') as file:
        return pickle.load(file)

# Load model and encodings
model = load_model_locally()
user_to_user_encoded = load_encodings(Config.USER_ENCODING_PATH)
place_to_place_encoded = load_encodings(Config.PLACE_ENCODING_PATH)

# Load the place data from the CSV file globally
place_data_df = pd.read_csv(Config.PLACE_DATA_PATH)


@model_bp.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    userId = data['userId']

    # new_user = get_all_users()
    new_rating = get_all_ratings(userId)
    
    # Mengonversi data ke DataFrame
    # new_user_df = pd.DataFrame(new_user)
    new_rating_df = pd.DataFrame(new_rating)
    place_df = pd.read_csv(Config.PLACE_DATA_PATH)
    
    # Menampilkan beberapa baris pertama dari data baru untuk memastikan terbaca dengan benar
    # print(new_user_df.head())
    # print(new_rating_df.head())

    new_rating_merged = pd.merge(new_rating_df, place_df, on='Place_Id', how='left')

    # Menampilkan beberapa baris pertama dari data yang digabungkan untuk memastikan penggabungan benar
    # print(new_rating_merged.head())
    
    # Menggabungkan data baru dengan user data sebelumnya
    # new_user_encoded = new_user_df.copy()
    # new_user_encoded['user'] = new_user_encoded['User_Id'].map(user_to_user_encoded)

    # Lakukan encoding pada User_Id dan Place_Id untuk data rating baru
    new_rating_merged['user'] = new_rating_merged['User_Id'].map(user_to_user_encoded)
    new_rating_merged['place'] = new_rating_merged['Place_Id'].map(place_to_place_encoded)

    # Menghapus baris dengan nilai NaN akibat Place_Id atau User_Id yang tidak ada dalam dictionary
    new_rating_merged = new_rating_merged.dropna(subset=['user', 'place'])

    # Melakukan prediksi dengan model
    predictions = model.predict([new_rating_merged['user'], new_rating_merged['place']])

    # Menambahkan hasil prediksi ke DataFrame
    new_rating_merged['predicted_rating'] = predictions.flatten()

    # Menampilkan hasil prediksi
    # print(new_rating_merged[['User_Id', 'Place_Id', 'Place_Name', 'Category', 'predicted_rating']])
    
    df_top_recommendations = new_rating_merged.sort_values(by='predicted_rating', ascending=False).head(9)

    # Fetch place details for each recommendation
    detailed_recommendations = []
    for _, row in df_top_recommendations.iterrows():
        place_id = int(row['Place_Id'])  # Convert place_id to integer
            
        # Check if the place ID exists in the place data
        if place_id not in place_data_df['Place_Id'].values:
            continue
            
        place_info, status_code = getPlace(place_id)
        if status_code == 200:
            detailed_recommendations.append(place_info)
        else:
            detailed_recommendations.append({'error': f'Place ID {place_id} not found', 'placeId': place_id})
            
    return jsonify(detailed_recommendations)

# @model_bp.route('/recommend', methods=['POST'])
# def recommend():
#     data = request.get_json()
#     user_id = data['user_id']
    
#     uid_model, status_code_uid_model = get_uid_model(user_id)
#     if status_code_uid_model == 200:
#         # Ensure user_id exists in the encoded data
#         if uid_model not in user_to_user_encoded:
#             return jsonify({'error': f'User ID {uid_model} not found'}), 404

#         # Get user encoding
#         user_encoding = user_to_user_encoded[uid_model]

#         # Create DataFrame with user and all place encodings
#         all_places = np.array(list(place_to_place_encoded.values()))
#         user_input = np.repeat(np.array([user_encoding]), len(all_places), axis=0)

#         # Predict ratings for all places
#         predictions = model.predict([user_input, all_places])

#         # Create DataFrame with predictions and place encodings
#         df_predictions = pd.DataFrame({
#             'place': list(place_to_place_encoded.keys()),
#             'predicted_rating': predictions.flatten()
#         })

#         # Sort by predicted rating and get top 10 recommendations
#         df_top_recommendations = df_predictions.sort_values(by='predicted_rating', ascending=False).head(9)

#         # Fetch place details for each recommendation
#         detailed_recommendations = []
#         for _, row in df_top_recommendations.iterrows():
#             place_id = int(row['place'])  # Convert place_id to integer
            
#             # Check if the place ID exists in the place data
#             if place_id not in place_data_df['Place_Id'].values:
#                 continue
            
#             place_info, status_code = getPlace(place_id)
#             if status_code == 200:
#                 # Fetch reviews data for the place from Firestore
#                 reviews_data = get_reviews(place_id)
                
#                 # Calculate average rating using reviews_data
#                 average_rating = calculate_rating(reviews_data)
                
#                 # Add average_rating to place_info
#                 place_info['average_rating'] = average_rating
#                 detailed_recommendations.append(place_info)
#             else:
#                 detailed_recommendations.append({'error': f'Place ID {place_id} not found', 'placeId': place_id})

#     return jsonify(detailed_recommendations)