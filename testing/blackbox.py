# from flask import Flask, request, jsonify
# import numpy as np
# import tensorflow as tf

# app = Flask(__name__)

# # Load the saved model
# model = tf.keras.models.load_model('model.h5', compile=False)

# @app.route('/model', methods=['GET'])
# def get_model():
#     # Get the model architecture and weights
#     model_architecture = model.to_json()
#     model_weights = model.get_weights()

#     # Return the model architecture and weights as a JSON response
#     return jsonify({
#         'architecture': model_architecture,
#         'weights': [weight.tolist() for weight in model_weights]
#     })

# if __name__ == '__main__':
#     app.run(debug=True)