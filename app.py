from flask import Flask, request, jsonify
import tensorflow as tf
import joblib
import numpy as np
import pandas as pd
from google.cloud import firestore
from google.cloud import storage
import os
import urllib.parse

app = Flask(__name__)

BUCKET_NAME='tourid-bucket'
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "firestore-config.json"
credentials = storage.Client.from_service_account_json('bucket/bucket-config.json')

# SERVICE_ACCOUNT_KEY_FILE = 'bucket/bucket-config.json'

# Initialize the Google Cloud Storage client using the service account JSON key file
# storage_client = storage.Client.from_service_account_json(SERVICE_ACCOUNT_KEY_FILE)

# Initialize Firestore DB
db = firestore.Client(project='capstone-tourid', database='tourid')

# Load the pre-trained model
model = tf.keras.models.load_model('best_model.h5', custom_objects={'mse': tf.keras.losses.MeanSquaredError()})

# Load dictionary encodings with joblib
user_to_user_encoded = joblib.load('user_to_user_encoded.pkl')
place_to_place_encoded = joblib.load('place_to_place_encoded.pkl')

# Load the place data CSV
place_data = pd.read_csv('place_data.csv')

# def generate_signed_url(bucket_name, blob_name, expiration_time=900):
#     """Generate a signed URL for a GCS object."""
#     bucket = storage_client.bucket(bucket_name)
#     blob = bucket.blob(blob_name)
#     url = blob.generate_signed_url(expiration=expiration_time)
#     return url

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    user_id = data.get('user_id')
    place_id = data.get('place_id')

    user_encoded = user_to_user_encoded.get(user_id, None)
    place_encoded = place_to_place_encoded.get(place_id, None)

    if user_encoded is None or place_encoded is None:
        return jsonify({'error': 'User or Place not found'}), 400

    # Convert the inputs to numpy arrays and reshape them appropriately
    user_input = np.array([user_encoded]).reshape(1, -1)
    place_input = np.array([place_encoded]).reshape(1, -1)

    # Predict the rating
    prediction = model.predict([user_input, place_input])
    rating = float(prediction[0][0])  # Convert numpy.float32 to Python float

    return jsonify({'rating': rating})

@app.route('/top-rated', methods=['GET'])
def top_rated():
    # Sort the places by their rating in descending order
    sorted_places = place_data.sort_values(by='Rating', ascending=False)

    # Select the top 20 places
    top_rated_places = sorted_places.head(20)

    # Prepare the response with the required fields
    response = []
    for _, row in top_rated_places.iterrows():
        place_id = row['Place_Id']
        place_name = row['Place_Name']
        city = row['City']
        rating = row['Rating']
        
        # Encode the place name to handle whitespace
        encoded_place_name = urllib.parse.quote(place_name)
        
        # Construct the public image URL
        image_url = f'https://storage.googleapis.com/{BUCKET_NAME}/images/{encoded_place_name}.jpg'
        
        # Append the place details and image URL to the response list
        response.append({
            'Place_Id': place_id,
            'Place_Name': place_name,
            'City': city,
            'Rating': rating,
            'Image_URL': image_url
        })

    return jsonify(response)

# Define categories
categories = ['Budaya', 'Taman Hiburan', 'Cagar Alam', 'Bahari', 'Pusat Perbelanjaan', 'Ibadah']

@app.route('/top-rated/<category>', methods=['GET'])
def top_rated_by_category(category):
    if category not in categories:
        return jsonify({'error': 'Invalid category'}), 400

    # Filter places by the specified category
    category_places = place_data[place_data['Category'] == category]

    # Sort places within the category by rating in descending order
    sorted_places = category_places.sort_values(by='Rating', ascending=False)

    # Select the top 20 places within the category
    top_rated_places = sorted_places.head(20)

    # Prepare the response with the required fields
    response = top_rated_places[['Place_Id', 'Place_Name', 'City', 'Rating']].to_dict(orient='records')

    return jsonify(response)

@app.route('/destination/<int:id>', methods=['GET'])
def get_destination_details(id):
    # Filter place by ID
    place = place_data[place_data['Place_Id'] == id]

    if place.empty:
        return jsonify({'error': 'Destination not found'}), 404

    # Get details of the destination
    name = place['Place_Name'].iloc[0]
    rating = place['Rating'].iloc[0]
    description = place['Description'].iloc[0]
    city = place['City'].iloc[0]

    # Prepare the response
    response = {
        'name': name,
        'rating': rating,
        'description': description,
        'city': city
    }

    return jsonify(response)

@app.route('/reviews/<int:id>', methods=['GET'])
def get_reviews(id):
    reviews = []

    # Query Firestore for all reviews
    reviews_ref = db.collection('reviews').stream()

    for review_doc in reviews_ref:
        # Get the username (user_id) from the document ID
        username = review_doc.id

        # Query the user's reviews
        user_reviews_ref = db.collection('reviews').document(username).collection('user_reviews').stream()

        for user_review_doc in user_reviews_ref:
            review_data = user_review_doc.to_dict()
            if review_data.get('place_id') == id:
                reviews.append(review_data)

    if not reviews:
        return jsonify({'message': 'There are no reviews yet for this destination.'}), 200

    return jsonify(reviews)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
