from flask import Flask, jsonify
from flask_cors import CORS
import logging
from app.extensions import db, jwt, limiter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    CORS(app)

    # Configuration
    # Use absolute path to ensure DB is found regardless of where run.py is executed
    import os
    basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    db_path = os.path.join(basedir, 'instance', 'sentiment.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'super-secret-key-change-this-in-production'

    # Initialize Extensions
    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.api import api_bp
    from app.routes.views import views_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(views_bp)

    # Create Database Tables
    with app.app_context():
        db.create_all()
        
    # Error handlers
    register_error_handlers(app)

    return app

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'status': 'error',
            'message': 'Endpoint tidak ditemukan'
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'status': 'error',
            'message': 'Method tidak diizinkan'
        }), 405

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'status': 'error',
            'message': 'Terjadi kesalahan internal server'
        }), 500
