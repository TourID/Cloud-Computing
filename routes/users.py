from flask import Blueprint, request, jsonify
from google.cloud import firestore
from config.config import Config

users_bp = Blueprint('users', __name__)
db = firestore.Client(project=Config.PROJECT, database=Config.DATABASE)
users_collection = db.collection('users')

@users_bp.route('/add-user', methods=['POST'])
def add_user():
    data = request.json
    try:
        userId = data.get('userId')
        email = data.get('email')
        
        # Mendapatkan nilai uid_model tertinggi saat ini
        highest_uid_model = 0
        users = users_collection.stream()
        for user in users:
            user_data = user.to_dict()
            if 'uid_model' in user_data:
                highest_uid_model = max(highest_uid_model, user_data['uid_model'])
        
        # Meng-increment nilai tertinggi untuk uid_model baru
        new_uid_model = highest_uid_model + 1

        # Simpan pengguna baru di Firestore
        db.collection('users').document(userId).set({
            'email': email,
            'uid_model': new_uid_model
        })

        return jsonify({'message': 'User created and data saved in Firestore'}), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 400

def get_uid_model(userId):
    try:
        if not userId:
            return {'message': 'User ID not found'}, 400
        
        # Mendapatkan dokumen pengguna berdasarkan user_id
        user_doc = users_collection.document(userId).get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            uid_model = user_data.get('uid_model', None)
            if uid_model is not None:
                return uid_model, 200
            else:
                return {'message': 'uid_model not found for the user'}, 404
        else:
            return {'message': 'User not found'}, 404
    except Exception as e:
        return jsonify({'message': str(e)}), 400
    
# @users_bp.route('/get-uid-model/<userId>', methods=['GET'])
# def get_uid_model(userId):
#     try:
#         if not userId:
#             return jsonify({'message': 'User ID not found'}), 400
        
#         # Mendapatkan dokumen pengguna berdasarkan user_id
#         user_doc = db.collection('users').document(userId).get()
#         if user_doc.exists:
#             user_data = user_doc.to_dict()
#             uid_model = user_data.get('uid_model', None)
#             if uid_model is not None:
#                 return jsonify({'uid_model': uid_model}), 200
#             else:
#                 return jsonify({'message': 'uid_model not found for the user'}), 404
#         else:
#             return jsonify({'message': 'User not found'}), 404
#     except Exception as e:
#         return jsonify({'message': str(e)}), 400
    
# @users_bp.route('/add-user', methods=['POST'])
# def add_user():
#     try:
#         data = request.json
#         userId = data['userId']
#         username = data['username']
#         email = data['email']
#         user_doc_ref = users_collection.document(userId)
#         new_user_doc = {'username': username, 'email':email}
#         user_doc_ref.set(new_user_doc)
#         return jsonify({"success": True, "message": "User added successfully."}), 200

#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)}), 400
    
# @users_bp.route('/detail-user/<string:userId>', methods=['GET'])
# def detail_user(userId):
#     try:
#         user_doc_ref = users_collection.document(userId)
#         user_doc = user_doc_ref.get()

#         if user_doc.exists:
#             user_data = user_doc.to_dict()
#             return jsonify(user_data), 200
#         else:
#             return jsonify({"success": False, "message": "User not found."}), 404

#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)}), 400