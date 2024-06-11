from flask import Blueprint, jsonify
import pandas as pd
from config.config import Config
import urllib.parse

places_bp = Blueprint('places', __name__)
place_data = pd.read_csv(Config.PLACE_DATA_PATH)

@places_bp.route('/top-rated', methods=['GET'])
def top_rated():
    sorted_places = place_data.sort_values(by='Rating', ascending=False)
    top_rated_places = sorted_places.head(20)
    response = []

    for _, row in top_rated_places.iterrows():
        place_id = row['Place_Id']
        place_name = row['Place_Name']
        city = row['City']
        rating = row['Rating']
        encoded_place_name = urllib.parse.quote(place_name)
        image_url = f'https://storage.googleapis.com/{Config.BUCKET_NAME}/images/{encoded_place_name}.jpg'
        response.append({
            'Place_Id': place_id,
            'Place_Name': place_name,
            'City': city,
            'Rating': rating,
            'Image_URL': image_url
        })

    return jsonify(response)

@places_bp.route('/top-rated/<category>', methods=['GET'])
def top_rated_by_category(category):
    categories = ['Budaya', 'Taman Hiburan', 'Cagar Alam', 'Bahari', 'Pusat Perbelanjaan', 'Ibadah']
    if category not in categories:
        return jsonify({'error': 'Invalid category'}), 400

    category_places = place_data[place_data['Category'] == category]
    sorted_places = category_places.sort_values(by='Rating', ascending=False)
    top_rated_places = sorted_places.head(20)
    response = top_rated_places[['Place_Id', 'Place_Name', 'City', 'Rating']].to_dict(orient='records')

    return jsonify(response)
