from flask import Flask, jsonify, request
from tensorflow.keras.models import load_model
import tensorflow as tf
import numpy as np

app = Flask(__name__)

# Load the Keras model
model = load_model('best_model.h5', custom_objects={'mse': tf.keras.losses.MeanSquaredError()})

# Encoder dictionaries
# INI PLS INI GABISA PADAHAL UDAH SAMA
# CEK INI YA
# hiks
# ini dari ipynb btw gatau gimana cara encode nya 
user_to_user_encoded = {}  # Isi dengan dictionary yang digunakan untuk encoding user
place_to_place_encoded = {}  # Isi dengan dictionary yang digunakan untuk encoding place
top_rated_places = {}

# place_encoded_to_place = {v: k for k, v in place_to_place_encoded.items()}

# Function to get places data from the model
# ini yg masih data dummy
def get_places_from_model():
    # Assuming the model returns ratings for each destination
    num_destinations = 10  # Change this to the number of destinations you want to recommend
    ratings = np.random.rand(num_destinations)  # Dummy ratings
    
    # Assuming your destinations data is stored in a list of dictionaries
    destinations = {}
    for i in range(num_destinations):
        destination = {
            'Places_Id': i,
            'Place_Name': f'Destination {i}',
            'rating': ratings[i],
            # Add other destination attributes as needed
        }
        destinations.append(destination)
    
    # Sort destinations by rating in descending order
    destinations.sort(key=lambda x: x['rating'], reverse=True)
    
    return destinations

# Endpoint to get top-rated destinations
# ini gabisa T___T
@app.route('/top-rated-destinations', methods=['GET'])
def top_rated_destinations():
    # Get top-rated destinations from the model
    top_rated_places = []

    # Assume model returns top-rated places in the format: [(place_id, place_name, rating), ...]
    top_rated_data = model.get_top_rated_destinations()  

    # Iterate over the top-rated data and format it as dictionaries
    for place_id, place_name, rating in top_rated_data:
        top_rated_places.append({
            'place_id': place_id,
            'place_name': place_name,
            'rating': rating
        })

    # Check if there are no top-rated places
    if not top_rated_places:
        return jsonify({'error': 'No top-rated destinations found'}), 404

    # Prepare the response with top-rated destinations
    response = jsonify(top_rated_places)

    return response

#also gabisa
@app.route('/places-by-rating', methods=['GET'])
def places_by_rating():
    # Use the model to retrieve places sorted by rating
    sorted_places = get_places_by_rating_from_model()

    # Format the retrieved data into a JSON response
    formatted_places = []
    for place in sorted_places:
        formatted_places.append({
            'place_name': place['place_name'],
            'rating': place['rating']
        })

    # Return the formatted data as JSON
    return jsonify(formatted_places)

# Function to get places sorted by rating from the model using model.predict
def get_places_by_rating_from_model():
    # Example: Use model.predict to predict ratings for each place
    # Replace this with your actual logic to predict ratings
    place_features = {}  # Replace ... with the actual features of the places
    ratings = model.predict(place_features)

    # Assuming you have a list of place names corresponding to the predictions
    place_names = {}  # Replace [...] with the actual list of place names

    # Combine place names and predicted ratings
    places = {}
    for place_name, rating in zip(place_names, ratings):
        places.append({
            'place_name': place_name,
            'rating': rating[0]  # Assuming ratings are scalar values
        })

    # Sort places by predicted rating
    sorted_places = sorted(places, key=lambda x: x['rating'], reverse=True)
    return sorted_places

# ini udah ikutin notebook tetep sama, kemungkinan besar karena user_to_user_encode sama place_to_place_encode nya gajalan
@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    user_id = data['user_id']
    place_id = data['place_id']

    user_encoded = user_to_user_encoded.get(user_id, None)
    place_encoded = place_to_place_encoded.get(place_id, None)

    if user_encoded is None or place_encoded is None:
        return jsonify({'error': 'User or Place not found'}), 400

    prediction = model.predict([[user_encoded], [place_encoded]])
    rating = prediction[0][0]

    user_encoded = np.array([[user_encoded]])
    place_encoded = np.array([[place_encoded]])

    return jsonify({'rating': rating})

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
