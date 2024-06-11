from flask import Blueprint, request, jsonify
import numpy as np
from models.model import model
from models.encodings import user_to_user_encoded, place_to_place_encoded

predict_bp = Blueprint('predict', __name__)

@predict_bp.route('/predict', methods=['POST'])
def predict():
    data = request.json
    user_id = data.get('user_id')
    place_id = data.get('place_id')

    user_encoded = user_to_user_encoded.get(user_id, None)
    place_encoded = place_to_place_encoded.get(place_id, None)

    if user_encoded is None or place_encoded is None:
        return jsonify({'error': 'User or Place not found'}), 400

    user_input = np.array([user_encoded]).reshape(1, -1)
    place_input = np.array([place_encoded]).reshape(1, -1)

    prediction = model.predict([user_input, place_input])
    rating = float(prediction[0][0])

    return jsonify({'rating': rating})
