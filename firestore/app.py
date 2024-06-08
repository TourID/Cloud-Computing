# app.py
from flask import Flask, request, jsonify
from google.cloud import firestore
import os

app = Flask(__name__)

# Set environment variable for Google Application Credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "firestore/firestore-service-account.json"

# Initialize Firestore DB
db = firestore.Client(project='capstone-tourid', database='tourid')
reviews_collection = db.collection('reviews')
reviews_collection_group = db.collection_group('user_reviews')

@app.route('/add-review', methods=['POST'])
def add_review():
    try:
        data = request.json
        user_id = data['user_id']
        username = data['username']
        place_id = data['place_id']
        rating = data['rating']
        review_text = data['review']
        
        # Reference to the user's document
        user_doc_ref = reviews_collection.document(user_id)
        new_user_doc = {
            'username' : username
        }
        user_doc_ref.set(new_user_doc)
        
        # Create or update the sub-collection for reviews
        user_reviews_subcollection = user_doc_ref.collection('user_reviews')
        new_review_data = {
            'place_id': place_id,
            'rating': rating,
            'review': review_text
        }
        # Add new review document to the sub-collection with a unique ID
        user_reviews_subcollection.add(new_review_data)
        
        return jsonify({"success": True, "message": "Review added successfully."}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400
    
@app.route('/get-reviews-by-place/<place_id>', methods=['GET'])
def get_reviews_by_place(place_id):
    try:
        place_id = int(place_id)
        
        # Query reviews collection for documents with place_id
        reviews_query = reviews_collection_group.where('place_id', '==', place_id).stream()
        
        reviews_data = []
        for review_doc in reviews_query:
           # Get the parent document (user document) reference
            parent_ref = review_doc.reference.parent.parent
            
            # Get the user document
            user_doc = parent_ref.get()
            user_data = user_doc.to_dict()
            
            # Get the user_id and username from the user document
            user_id = parent_ref.id
            username = user_data.get('username', 'Unknown')  # Default to 'Unknown' if username is not found
            
            # Get the review data
            review_data = review_doc.to_dict()
            review_data['user_id'] = user_id
            review_data['username'] = username
            
            reviews_data.append(review_data)
        
        return jsonify({"success": True, "data": reviews_data}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
