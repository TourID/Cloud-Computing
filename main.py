from flask import Flask, jsonify
import h5py
import json

app = Flask(__name__)

# Function to recursively extract datasets from HDF5 file
def extract_datasets(group):
    data = {}
    for key, item in group.items():
        if isinstance(item, h5py.Dataset):
            data[key] = item[()].tolist()
        elif isinstance(item, h5py.Group):
            data[key] = extract_datasets(item)
    return data

# Function to load model weights and architecture from HDF5
def load_model_from_h5(file_path):
    with h5py.File(file_path, 'r') as f:
        # Extract the model architecture
        model_config = json.loads(f.attrs['model_config'])  # No need to decode
        
        # Extract the model weights
        model_weights = extract_datasets(f)
    
    # Return architecture and weights as dictionary
    return model_config, model_weights

# Load the model (replace 'model.h5' with the path to your model)
model_config, model_weights = load_model_from_h5('model.h5')

@app.route('/')
def index():
    if model_config:
        return jsonify({"message": "Model loaded successfully!"})
    else:
        return jsonify({"message": "Failed to load the model."}), 500

@app.route('/model')
def get_model():
    if model_config:
        return jsonify({
            "model_config": model_config,
            "model_weights": model_weights
        })
    else:
        return jsonify({"message": "Model not loaded."}), 500

if __name__ == '__main__':
    app.run(debug=True)
