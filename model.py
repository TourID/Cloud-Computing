from flask import Flask, jsonify
from tensorflow.keras.models import load_model
import tensorflow as tf
import numpy as np

app = Flask(__name__)

# Load the Keras model
model = load_model('best_model.h5', custom_objects={'mse': tf.keras.losses.MeanSquaredError()})

# Function to get places data from the model
def get_places_from_model():
    # Assuming the model returns ratings for each destination
    num_destinations = 10  # Change this to the number of destinations you want to recommend
    ratings = np.random.rand(num_destinations)  # Dummy ratings
    
    # Assuming your destinations data is stored in a list of dictionaries
    destinations = []
    for i in range(num_destinations):
        destination = {
            'id': i,
            'places_name': f'Destination {i}',
            'rating': ratings[i],
            # Add other destination attributes as needed
        }
        destinations.append(destination)
    
    # Sort destinations by rating in descending order
    destinations.sort(key=lambda x: x['rating'], reverse=True)
    
    return destinations

# Endpoint to get top-rated destinations
@app.route('/top-rated-destinations', methods=['GET'])
def top_rated_destinations():
    # Get top-rated destinations from the model
    top_rated_places = get_places_from_model()
    
    # Return the top-rated destinations as JSON
    return jsonify(top_rated_places)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
