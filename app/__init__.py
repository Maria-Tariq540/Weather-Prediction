"""
Flask Application Factory
Creates and configures the Flask application instance.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from flask_session import Session
from config import config
import os

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
sess = Session()


def create_app(config_name=None):
    """
    Application factory function.
    
    Args:
        config_name: Configuration name ('development', 'testing', 'production')
    
    Returns:
        Flask application instance
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    sess.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # User loader callback
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.weather import weather_bp
    from app.routes.prediction import prediction_bp
    from app.routes.favorites import favorites_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(weather_bp, url_prefix='/api/weather')
    app.register_blueprint(prediction_bp, url_prefix='/api/predict')
    app.register_blueprint(favorites_bp, url_prefix='/api/favorites')
    
    # Register main routes (HTML pages)
    from app.routes import main
    app.register_blueprint(main.main_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create necessary directories
        os.makedirs(app.config['MODEL_PATH'], exist_ok=True)
        os.makedirs(os.path.join(app.root_path, 'static', 'images', 'weather-icons'), exist_ok=True)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal server error'}, 500
    
    return app
