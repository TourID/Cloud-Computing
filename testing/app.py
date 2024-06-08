from flask import Flask, request, jsonify
import tensorflow as tf
from tensorflow.keras.models import load_model
import numpy as np

app = Flask(__name__)

# Path ke file model yang disimpan
MODEL_PATH = 'best_model.h5'

# Memuat model
model = load_model(MODEL_PATH, compile=False)

# Contoh data tempat wisata (sebagai contoh)
places_data = {
    1: {'name': 'Wisata Alam Mangrove Angke', 'category': 'Cagar Alam', 'price': 25000, 'rating': 4.3},
    2: {'name': 'Gembira Loka Zoo', 'category': 'Cagar Alam', 'price': 60000, 'rating': 4.5},
    # Tambahkan data tempat wisata lainnya di sini
}

@app.route('/places/<int:place_id>', methods=['GET'])
def get_place_info(place_id):
    if place_id in places_data:
        place_info = places_data[place_id]
        return jsonify(place_info)
    else:
        return jsonify({'error': 'Place not found'}), 404
    
@app.route('/model-summary', methods=['GET'])
def model_summary():
    # Membuat ringkasan model
    stringlist = []
    model.summary(print_fn=lambda x: stringlist.append(x))
    summary = "\n".join(stringlist)
    
    # Mengembalikan ringkasan model dalam format JSON
    return jsonify({"model_summary": summary})

@app.route('/predict', methods=['POST'])
def predict():
    # Dapatkan data input dari request
    data = request.get_json()
    
    # Asumsikan data memiliki format {'user_id': ..., 'place_id': ...}
    user_id = data['user_id']
    place_id = data['place_id']
    
    # Lakukan prediksi
    prediction = model.predict([np.array([user_id]), np.array([place_id])])
    
    # Kembalikan hasil prediksi, konversi menjadi float
    return jsonify({"prediction": float(prediction[0][0])})

if __name__ == '__main__':
    app.run(debug=True)
