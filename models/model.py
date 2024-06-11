import tensorflow as tf
from config.config import Config

model = tf.keras.models.load_model(Config.MODEL_PATH, custom_objects={'mse': tf.keras.losses.MeanSquaredError()})
