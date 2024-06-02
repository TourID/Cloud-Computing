from flask import Flask, jsonify, request
import h5py

app = Flask(__name__)

# Function to load model weights and architecture from HDF5
def load_model_from_h5(file_path):
    with h5py.File(file_path, 'r') as f:
        # Extract the model architecture and weights
        model_loaded = f.attrs.get('model_config')
        model_weights = f.attrs.get('model_weights')
    
    # Return architecture and weights
    return model_loaded, model_weights

# Load the model (replace 'model.h5' with the path to your model)
model_loaded, model_weights = load_model_from_h5('model.h5')

@app.route('/')
def index():
    if model_loaded:
        return jsonify({"message": "Model loaded successfully!"})
    else:
        return jsonify({"message": "Failed to load the model."}), 500


if __name__ == '__main__':
    app.run(debug=True)