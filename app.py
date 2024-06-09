from flask import Flask, request, jsonify
import tensorflow as tf
import joblib
import numpy as np

app = Flask(__name__)

# Muat model terlatih
model = tf.keras.models.load_model('best_model.h5', custom_objects={'mse': tf.keras.losses.MeanSquaredError()})

# Muat dictionary encoding
user_to_user_encoded = joblib.load('user_to_user_encoded.pkl')
place_to_place_encoded = joblib.load('place_to_place_encoded.pkl')

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

if __name__ == '__main__':
    app.run(debug=True)