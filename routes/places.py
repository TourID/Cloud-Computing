
from flask import Blueprint, jsonify, request
import pandas as pd
from config.config import Config
import urllib.parse
from routes.reviews import get_reviews, calculate_rating
from config.gcs import generate_signed_url

places_bp = Blueprint('places', __name__)
place_data = pd.read_csv(Config.PLACE_DATA_PATH)

@places_bp.route('/tourism/<category>', methods=['GET'])
def tourism_by_category(category):
    categories = ['All', 'Budaya', 'Taman Hiburan', 'Cagar Alam', 'Bahari', 'Pusat Perbelanjaan', 'Ibadah']
    if category not in categories:
        return jsonify({'error': 'Invalid category'}), 400
    
    response = []
    
    if category == 'All':
        # sorted_places = place_data.sort_values(by='Rating', ascending=False)
        
        place_data_clean = place_data.dropna(subset=['Place_Id'])

        place_data_clean['New_Rating'] = place_data_clean['Place_Id'].apply(lambda pid: calculate_rating(get_reviews(int(pid))))
        # Sort places by new rating
        sorted_places = place_data_clean.sort_values(by='New_Rating', ascending=False)
        for _, row in sorted_places.iterrows():
            reviews_data = get_reviews(int(row['Place_Id']))
            rating = calculate_rating(reviews_data)
            
            blob_name = f"images/{row['Place_Name']}.jpg"
            image_url = generate_signed_url(Config.BUCKET_NAME, blob_name)
            # print(f"Blob Name: {blob_name}, Signed URL: {image_url}")
            
            response.append({
                'Place_Id': int(row['Place_Id']),
                'Place_Name': row['Place_Name'],
                'City': row['City'],
                'Category': row['Category'],
                'Rating': rating,
                'Image_URL': image_url
            })
            
        return jsonify(response)
    else:
        category_places = place_data[place_data['Category'] == category]
        category_places['New_Rating'] = category_places['Place_Id'].apply(lambda pid: calculate_rating(get_reviews(int(pid))))
        sorted_places = category_places.sort_values(by='New_Rating', ascending=False)
        
        top_rated_places = sorted_places.head(20)
        for _, row in top_rated_places.iterrows():
            reviews_data = get_reviews(int(row['Place_Id']))
            rating = calculate_rating(reviews_data)
            
            blob_name = f"images/{row['Place_Name']}.jpg"
            image_url = generate_signed_url(Config.BUCKET_NAME, blob_name)
            
            response.append({
                'Place_Id': int(row['Place_Id']),
                'Place_Name': row['Place_Name'],
                'City': row['City'],
                'Category': row['Category'],
                'Rating': rating,
                'Image_URL': image_url
            })

        return jsonify(response)

@places_bp.route('/detail-tourism/<int:id>', methods=['GET'])
def get_destination_details_with_reviews(id):
    place = place_data[place_data['Place_Id'] == id]
    if place.empty:
        return jsonify({'error': 'Destination not found'}), 404

    name = place['Place_Name'].iloc[0]
    description = place['Description'].iloc[0]
    category = place['Category'].iloc[0]
    city = place['City'].iloc[0]
    price = place['Price'].iloc[0]
    lat = place['Lat'].iloc[0]
    long = place['Long'].iloc[0]

    try:
        reviews_data = get_reviews(id)
        average_rating = calculate_rating(reviews_data)

        blob_name = f"images/{name}.jpg"
        image_url = generate_signed_url(Config.BUCKET_NAME, blob_name)
        
        response = {
            'Place_Name': name,
            'Description': description,
            'Category' : category,
            'City': city,
            'Price': price,
            'Latitude' : lat,
            'Longtitude' : long,
            'Rating_Location': average_rating,
            'Reviews': reviews_data,
            'Image_URL' : image_url
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@places_bp.route('/search', methods=['GET'])
def search_places():
    query = request.args.get('query', '')

    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400

    search_results = place_data[place_data['Place_Name'].str.contains(query, case=False, na=False)]
    response = search_results[['Place_Name', 'Rating', 'City']].to_dict(orient='records')

    return jsonify(response)


# @places_bp.route('/top-rated', methods=['GET'])
# def top_rated():
#     sorted_places = place_data.sort_values(by='Rating', ascending=False)
#     top_rated_places = sorted_places.head(20)
#     response = []

#     for _, row in top_rated_places.iterrows():
#         reviews_data = get_reviews(int(row['Place_Id']))
#         rating = calculate_rating(reviews_data)
        
#         blob_name = f"images/{row['Place_Name']}.jpg"
#         image_url = generate_signed_url(Config.BUCKET_NAME, blob_name)
#         # print(f"Blob Name: {blob_name}, Signed URL: {image_url}")
        
#         response.append({
#             'Place_Id': int(row['Place_Id']),
#             'Place_Name': row['Place_Name'],
#             'City': row['City'],
#             'Category': row['Category'],
#             'Price': row['Price'],
#             'Latitude': row['Lat'],
#             'Longtitude': row['Long'],
#             'Rating': rating,
#             'Image_URL': image_url
#         })

#     return jsonify(response)

# @places_bp.route('/top-rated/<category>', methods=['GET'])
# def top_rated_by_category(category):
#     categories = ['Budaya', 'Taman Hiburan', 'Cagar Alam', 'Bahari', 'Pusat Perbelanjaan', 'Ibadah']
#     if category not in categories:
#         return jsonify({'error': 'Invalid category'}), 400

#     category_places = place_data[place_data['Category'] == category]
#     sorted_places = category_places.sort_values(by='Rating', ascending=False)
#     top_rated_places = sorted_places.head(20)
#     response = top_rated_places[['Place_Id', 'Place_Name', 'City', 'Rating']].to_dict(orient='records')

#     return jsonify(response)

