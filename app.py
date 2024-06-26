from flask import Flask
from routes.users import users_bp
from routes.model import model_bp
from routes.places import places_bp
from routes.reviews import reviews_bp
from routes.bookmarks import bookmarks_bp
from config.config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Register blueprints
app.register_blueprint(users_bp)
app.register_blueprint(model_bp)
app.register_blueprint(places_bp)
app.register_blueprint(reviews_bp)
app.register_blueprint(bookmarks_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
