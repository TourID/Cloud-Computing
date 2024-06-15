from flask import Blueprint, request, jsonify
from google.cloud import firestore
from config.config import Config
from routes.places import getPlace

bookmarks_bp = Blueprint('bookmarks', __name__)
db = firestore.Client(project=Config.PROJECT, database=Config.DATABASE)
bookmarks_collection = db.collection('bookmarks')

@bookmarks_bp.route('/add-bookmark', methods=['POST'])
def add_bookmark():
    try:
        data = request.json
        userId = data['userId']
        placeId = data['placeId']
        bookmark_doc_ref = bookmarks_collection.document(userId)
        
        # Validasi bahwa placeId harus berupa integer
        if not isinstance(placeId, int):
            return jsonify({"success": False, "message": "placeId must be an integer."}), 400
        
        # Mendapatkan dokumen bookmark berdasarkan userId
        bookmark_doc = bookmark_doc_ref.get()
        
        if bookmark_doc.exists:
            # Jika dokumen sudah ada, tambahkan placeId ke array placeIds
            bookmark_data = bookmark_doc.to_dict()
            placeIds = bookmark_data.get('placeId', [])
            
            if placeId not in placeIds:
                placeIds.append(placeId)
                bookmark_doc_ref.update({'placeId': placeIds})
            else:
                return jsonify({"success": False, "message": "PlaceId already bookmarked."}), 400
        else:
            # Jika dokumen tidak ada, buat dokumen baru dengan placeId dalam array
            new_bookmark_doc = {'placeId': [placeId]}
            bookmark_doc_ref.set(new_bookmark_doc)
        
        return jsonify({"success": True, "message": "Bookmark added successfully."}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400
    
@bookmarks_bp.route('/get-bookmark/<string:userId>', methods=['GET'])
def get_bookmarks(userId):
    try:
        if not userId:
            return jsonify({"success": False, "message": "userId is required"}), 400
        
        response = []
        
        bookmark_doc_ref = bookmarks_collection.document(userId)
        bookmark_doc = bookmark_doc_ref.get()

        if bookmark_doc.exists:
            bookmark_data = bookmark_doc.to_dict()
            placeIds = bookmark_data.get('placeId', [])
            for placeId in placeIds:
                place_data, status_code = getPlace(placeId)
                if status_code == 200:
                    response.append(place_data)
                else:
                    return jsonify(place_data), status_code
            return jsonify(response), 200
        else:
            return jsonify({"success": False, "message": "No bookmarks found for this user."}), 404

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400
    
@bookmarks_bp.route('/delete-bookmark', methods=['DELETE'])
def delete_bookmark():
    try:
        data = request.json
        userId = data['userId']
        placeId = data['placeId']
        bookmark_doc_ref = bookmarks_collection.document(userId)

        # Validasi bahwa placeId harus berupa integer
        if not isinstance(placeId, int):
            return jsonify({"success": False, "message": "placeId must be an integer."}), 400

        # Mendapatkan dokumen bookmark berdasarkan userId
        bookmark_doc = bookmark_doc_ref.get()

        if bookmark_doc.exists:
            bookmark_data = bookmark_doc.to_dict()
            placeIds = bookmark_data.get('placeId', [])

            if placeId in placeIds:
                placeIds.remove(placeId)
                if placeIds:
                    bookmark_doc_ref.update({'placeId': placeIds})
                else:
                    bookmark_doc_ref.delete()
                return jsonify({"success": True, "message": "Bookmark deleted successfully."}), 200
            else:
                return jsonify({"success": False, "message": "PlaceId not found in bookmarks."}), 404
        else:
            return jsonify({"success": False, "message": "No bookmarks found for this user."}), 404

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400