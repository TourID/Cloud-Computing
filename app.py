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
credentials = storage.Client.from_service_account_json('bucket-config.json')

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
def get_destination_details_with_reviews(id):
    # Assume place_data is a DataFrame loaded with destination details
    # Filter place by ID
    place = place_data[place_data['Place_Id'] == id]

    if place.empty:
        return jsonify({'error': 'Destination not found'}), 404

    # Get details of the destination
    name = place['Place_Name'].iloc[0]
    description = place['Description'].iloc[0]
    city = place['City'].iloc[0]

    reviews_collection_group = db.collection_group('user_reviews')
    
    try:
        # Query reviews collection for documents with place_id
        reviews_query = reviews_collection_group.where('place_id', '==', id).stream()
        
        reviews_data = []
        total_rating = 0
        total_reviews = 0
        
        for review_doc in reviews_query:
            # Get the parent document (user document) reference
            parent_ref = review_doc.reference.parent.parent
            
            # Get the user document
            user_doc = parent_ref.get()
            user_data = user_doc.to_dict()
            
            # Get the user_id and username from the user document
            user_id = parent_ref.id
            username = user_data.get('username', 'Unknown')  # Default to 'Unknown' if username is not found
            
            # Get the review data
            review_data = review_doc.to_dict()
            review_data['user_id'] = user_id
            review_data['username'] = username
            
            reviews_data.append(review_data)
        
            total_rating += review_data['rating']
            total_reviews += 1
            
        average_rating = total_rating / total_reviews if total_reviews > 0 else 0

        # Prepare the response
        response = {
            'name': name,
            'description': description,
            'city': city,
            'rating': average_rating,
            'reviews': reviews_data
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route('/add-review', methods=['POST'])
def add_review():
    reviews_collection = db.collection('reviews')
    
    try:
        data = request.json
        user_id = data['user_id']
        username = data['username']
        place_id = data['place_id']
        rating = data['rating']
        review_text = data['review']
        
        # Reference to the user's document
        user_doc_ref = reviews_collection.document(user_id)
        new_user_doc = {
            'username' : username
        }
        user_doc_ref.set(new_user_doc)
        
        # Create or update the sub-collection for reviews
        user_reviews_subcollection = user_doc_ref.collection('user_reviews')
        new_review_data = {
            'place_id': place_id,
            'rating': rating,
            'review': review_text
        }
        # Add new review document to the sub-collection with a unique ID
        user_reviews_subcollection.add(new_review_data)
        
        return jsonify({"success": True, "message": "Review added successfully."}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

# @app.route('/reviews/<int:id>', methods=['GET'])
# def get_reviews(id):
#     reviews = []

#     # Query Firestore for all reviews
#     reviews_ref = db.collection('reviews').stream()

#     for review_doc in reviews_ref:
#         # Get the username (user_id) from the document ID
#         user_id = review_doc.id
        
#          # Get the user document
#         user_doc = db.collection('reviews').document(user_id).get()
#         user_data = user_doc.to_dict()
        
#         if not user_data:
#             continue

#         # Get the username from the user document
#         username = user_data.get('username', 'Unknown')  # Default to 'Unknown' if username is not found
        
#         # Query the user's reviews
#         user_reviews_ref = db.collection('reviews').document(user_id).collection('user_reviews').stream()

#         for user_review_doc in user_reviews_ref:
#             review_data = user_review_doc.to_dict()
#             if review_data.get('place_id') == id:
#                 review_data['user_id'] = user_id
#                 review_data['username'] = username
#                 reviews.append(review_data)
                
#                 total_rating += review_data['rating']
#                 total_reviews += 1

#     if not reviews:
#         return jsonify({'message': 'There are no reviews yet for this destination.', 'average_rating' : '0.0'}), 200

#     return jsonify(reviews)