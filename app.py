from flask import Flask
from routes.predict import predict_bp
from routes.places import places_bp
from routes.reviews import reviews_bp
from routes.users import users_bp
from config.config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Register blueprints
app.register_blueprint(predict_bp)
app.register_blueprint(places_bp)
app.register_blueprint(reviews_bp)
app.register_blueprint(users_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
