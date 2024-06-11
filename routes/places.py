from flask import Blueprint, jsonify, request
import pandas as pd
from config.config import Config
import urllib.parse
from routes.reviews import get_reviews, calculate_rating
from config.gcs import generate_signed_url

places_bp = Blueprint('places', __name__)
place_data = pd.read_csv(Config.PLACE_DATA_PATH)

@places_bp.route('/top-rated', methods=['GET'])
def top_rated():
    sorted_places = place_data.sort_values(by='Rating', ascending=False)
    top_rated_places = sorted_places.head(20)
    response = []

    for _, row in top_rated_places.iterrows():
        reviews_data = get_reviews(int(row['Place_Id']))
        rating = calculate_rating(reviews_data)
        encoded_place_name = urllib.parse.quote(row['Place_Name'])
        blob_name = f"images/{row['Place_Name']}.jpg"
        image_url = generate_signed_url(Config.BUCKET_NAME, blob_name)
        # print(f"Blob Name: {blob_name}, Signed URL: {image_url}")
        # image_url = f'https://storage.googleapis.com/{Config.BUCKET_NAME}/images/{encoded_place_name}.jpg'
        response.append({
            'Place_Id': int(row['Place_Id']),
            'Place_Name': row['Place_Name'],
            'City': row['City'],
            'Category': row['Category'],
            'Price': row['Price'],
            'Latitude': row['Lat'],
            'Longtitude': row['Long'],
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

@places_bp.route('/search', methods=['GET'])
def search_places():
    query = request.args.get('query', '')

    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400

    search_results = place_data[place_data['Place_Name'].str.contains(query, case=False, na=False)]
    response = search_results[['Place_Name', 'Rating', 'City']].to_dict(orient='records')

    return jsonify(response)
