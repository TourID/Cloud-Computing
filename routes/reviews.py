from flask import Blueprint, request, jsonify
from google.cloud import firestore
from config.config import Config
import pandas as pd

reviews_bp = Blueprint('reviews', __name__)
db = firestore.Client(project=Config.PROJECT, database=Config.DATABASE)
place_data = pd.read_csv(Config.PLACE_DATA_PATH)

def get_reviews(id):
    reviews_collection_group = db.collection_group('user_reviews')
    reviews_query = reviews_collection_group.where('place_id', '==', id).stream()
    reviews_data = []

    for review_doc in reviews_query:
        parent_ref = review_doc.reference.parent.parent
        user_doc = parent_ref.get()
        user_data = user_doc.to_dict()
        user_id = parent_ref.id
        username = user_data.get('username', 'Unknown')
        review_data = review_doc.to_dict()
        review_data['user_id'] = user_id
        review_data['username'] = username
        reviews_data.append(review_data)

    return reviews_data


def calculate_rating(reviews_data):
    total_rating = 0
    total_reviews = len(reviews_data)

    for review in reviews_data:
        total_rating += review['rating']

    average_rating = total_rating / total_reviews if total_reviews > 0 else 0
    return average_rating

@reviews_bp.route('/destination/<int:id>', methods=['GET'])
def get_destination_details_with_reviews(id):
    place = place_data[place_data['Place_Id'] == id]
    if place.empty:
        return jsonify({'error': 'Destination not found'}), 404

    name = place['Place_Name'].iloc[0]
    description = place['Description'].iloc[0]
    city = place['City'].iloc[0]

    try:
        reviews_data = get_reviews(id)
        average_rating = calculate_rating(reviews_data)

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

@reviews_bp.route('/add-review', methods=['POST'])
def add_review():
    reviews_collection = db.collection('reviews')
    try:
        data = request.json
        user_id = data['user_id']
        username = data['username']
        place_id = data['place_id']
        rating = data['rating']
        review_text = data['review']
        user_doc_ref = reviews_collection.document(user_id)
        new_user_doc = {'username': username}
        user_doc_ref.set(new_user_doc)
        user_reviews_subcollection = user_doc_ref.collection('user_reviews')
        new_review_data = {'place_id': place_id, 'rating': rating, 'review': review_text}
        user_reviews_subcollection.add(new_review_data)
        return jsonify({"success": True, "message": "Review added successfully."}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400
