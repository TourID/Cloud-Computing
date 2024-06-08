from flask import Flask, request, jsonify
import tensorflow as tf
from tensorflow.keras.models import load_model
import pandas as pd

# Load the trained model
model = load_model('best_model.h5', compile=False)

# Create the Flask application
app = Flask(__name__)

# Dummy data for places
# Dummy data for places and recommendations (should be replaced with actual data)
place_data = {
    'Place_Id': [1, 2, 3],
    'Place_Name': ['Place A', 'Place B', 'Dunia Fantasi'],
    'Category': ['Museum', 'Taman Hiburan', 'Taman Hiburan'],
    'Price': [100000, 150000, 270000],
    'Rating': [4.5, 4.2, 4.6]
}
place_df = pd.DataFrame(place_data)

recommendations_data = {
    'user': [1, 1, 2, 2, 3, 3],
    'place': [1, 2, 1, 3, 2, 3],
    'predicted_rating': [4.1, 4.7, 4.2, 4.8, 4.6, 4.9]
}
df_recommendations = pd.DataFrame(recommendations_data)

# Endpoint to get recommendation
@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()

    user_id = data.get('user_id')
    place_id = data.get('place_id')

    if user_id is None or place_id is None:
        return jsonify({'error': 'User ID and Place ID are required'}), 400

    # Prepare input data for the model
    user_input = tf.constant([[user_id]], dtype=tf.int32)
    place_input = tf.constant([[place_id]], dtype=tf.int32)

    # Get the prediction
    prediction = model.predict([user_input, place_input])
    rating = float(prediction[0][0])

    # Get place details
    place_details = places_data.get(place_id, {})

    response = {
        'user_id': user_id,
        'place_id': place_id,
        'predicted_rating': rating,
        'place_details': place_details
    }

    return jsonify(response)

def get_place_details(place_id):
    place_details = place_df[place_df['Place_Id'] == place_id]
    if not place_details.empty:
        return place_details.iloc[0].to_dict()
    return {}

# Endpoint to get top 10 recommendations for cultural places
@app.route('/top_cultural_recommendations', methods=['GET'])
def top_cultural_recommendations():
    # Group the recommendations by place and sort them by predicted rating in descending order
    grouped_recommendations = df_recommendations.groupby('place').apply(
        lambda x: x.sort_values(by='predicted_rating', ascending=False)
    ).reset_index(drop=True)
    
    # Collect the top 10 recommendations with the highest rating, considering only one recommendation per place
    top_recommendations = []
    seen_places = set()
    recommendations_count = 0

    for _, row in grouped_recommendations.iterrows():
        place_id = row['place']
        if place_id not in seen_places:
            place_details = get_place_details(place_id)
            category = place_details.get('Category')

            # Check if the place belongs to the 'Culture' category
            if category == 'Taman Hiburan':
                top_recommendations.append(place_details)
                seen_places.add(place_id)
                recommendations_count += 1

                if recommendations_count >= 10:
                    break

    return jsonify(top_recommendations)

if __name__ == '__main__':
    app.run(debug=True)