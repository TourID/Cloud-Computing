from flask import Blueprint, request, jsonify
from google.cloud import firestore
from config.config import Config
from routes.users import get_uid_model
import pandas as pd

reviews_bp = Blueprint('reviews', __name__)
db = firestore.Client(project=Config.PROJECT, database=Config.DATABASE)
place_data = pd.read_csv(Config.PLACE_DATA_PATH)

def get_reviews(place_id):
    reviews_collection = db.collection('reviews')
    review_docs = reviews_collection.stream()

    review_data_response = []

    for review_doc in review_docs:
        userId = review_doc.id
        review_data = review_doc.to_dict()
        username = review_data.get('username', 'Unknown')
        user_reviews_collection = reviews_collection.document(userId).collection('user_reviews')
        user_review_docs = user_reviews_collection.where('placeId', '==', place_id).stream()

        for user_review_doc in user_review_docs:
            user_review_data = user_review_doc.to_dict()
            user_review_data['userId'] = userId
            user_review_data['username'] = username
            review_data_response.append(user_review_data)

    return review_data_response
                
    # reviews_collection_group = db.collection_group('user_reviews')
    # reviews_query = reviews_collection_group.where('placeId', '==', id).stream()
    # reviews_data = []

    # for review_doc in reviews_query:
    #     parent_ref = review_doc.reference.parent.parent
    #     user_doc = parent_ref.get()
    #     user_data = user_doc.to_dict()
    #     user_id = parent_ref.id
    #     username = user_data.get('username', 'Unknown')
    #     review_data = review_doc.to_dict()
    #     review_data['userId'] = user_id
    #     review_data['username'] = username
    #     reviews_data.append(review_data)

    # return reviews_data


def calculate_rating(reviews_data):
    total_rating = 0
    total_reviews = len(reviews_data)

    for review in reviews_data:
        total_rating += review['rating']

    average_rating = total_rating / total_reviews if total_reviews > 0 else 0
    return average_rating

def get_all_ratings(userId):
    reviews_ref = db.collection('reviews').document(userId)
    user_reviews_ref = reviews_ref.collection('user_reviews')
    user_review_docs = user_reviews_ref.stream()

    ratings = []

    # Iterasi melalui setiap dokumen dalam sub-koleksi 'user_reviews'
    for user_review_doc in user_review_docs:
        user_review_data = user_review_doc.to_dict()
        place_id = user_review_data.get('placeId')
        rating = user_review_data.get('rating')
        uid_model = user_review_data.get('uid_model')
        if place_id and rating and uid_model:
            ratings.append({
                'Place_Id': place_id,
                'Place_Ratings': rating,
                'User_Id': uid_model
            })

    return ratings

@reviews_bp.route('/add-review', methods=['POST'])
def add_review():
    reviews_collection = db.collection('reviews')
    try:
        data = request.json
        user_id = data['userId']
        username = data['username']
        place_id = data['placeId']
        rating = data['rating']
        review_text = data['review']
        
        # Validasi bahwa placeId dan rating harus berupa integer
        if not isinstance(place_id, int):
            return jsonify({"success": False, "message": "placeId must be an integer."}), 400
        if not isinstance(rating, int):
            return jsonify({"success": False, "message": "rating must be an integer."}), 400
        
        user_doc_ref = reviews_collection.document(user_id)
        new_user_doc = {'username': username}
        user_doc_ref.set(new_user_doc, merge=True)
        user_reviews_subcollection = user_doc_ref.collection('user_reviews')
        
        #Cek apakah pengguna sudah mereview tempat ini
        query = user_reviews_subcollection.where('placeId', '==', place_id).get()
        if query:
            return jsonify({"success": False, "message": "User has already reviewed this place."}), 400
        
        #GET UID MODEL
        uid_model, status_code = get_uid_model(user_id)
        new_review_data = {'placeId': place_id, 'rating': rating, 'review': review_text, 'uid_model': uid_model}
        user_reviews_subcollection.add(new_review_data)
        return jsonify({"success": True, "message": "Review added successfully."}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400
