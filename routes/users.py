from flask import Blueprint, request, jsonify
from google.cloud import firestore
from config.config import Config

users_bp = Blueprint('users', __name__)
db = firestore.Client(project=Config.PROJECT, database=Config.DATABASE)
users_collection = db.collection('users')

@users_bp.route('/add-user', methods=['POST'])
def add_user():
    try:
        data = request.json
        user_id = data['user_id']
        username = data['username']
        email = data['email']
        user_doc_ref = users_collection.document(user_id)
        new_user_doc = {'username': username, 'email':email}
        user_doc_ref.set(new_user_doc)
        return jsonify({"success": True, "message": "User added successfully."}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400
    
@users_bp.route('/detail-user/<string:user_id>', methods=['GET'])
def detail_user(user_id):
    try:
        user_doc_ref = users_collection.document(user_id)
        user_doc = user_doc_ref.get()

        if user_doc.exists:
            user_data = user_doc.to_dict()
            return jsonify(user_data), 200
        else:
            return jsonify({"success": False, "message": "User not found."}), 404

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400