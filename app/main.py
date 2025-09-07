import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from flask import Flask, jsonify, render_template
from flask_cors import CORS
from app.api.sentiment_routes import sentiment_bp
from app.services.sentiment_analyzer import SentimentAnalyzer
from app.utils.error_handlers import register_error_handlers
import logging


def create_app():
    """Application factory pattern for Flask app"""
    app = Flask(__name__)
    
    # Configuration
    app.config['DEBUG'] = True
    app.config['JSON_SORT_KEYS'] = False
    
    # Enable CORS for all routes
    CORS(app, origins=['http://localhost:5000', 'http://127.0.0.1:5000'])
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize sentiment analyzer (this will load the model)
    try:
        app.sentiment_analyzer = SentimentAnalyzer()
        app.logger.info("Sentiment analyzer initialized successfully")
    except Exception as e:
        app.logger.error(f"Failed to initialize sentiment analyzer: {e}")
        raise
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    app.register_blueprint(sentiment_bp, url_prefix='/api/v1')
    
    # Web interface route
    @app.route('/')
    def index():
        """Serve the main web interface"""
        return render_template('index.html')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'Review Sentiment Analysis API',
            'version': '1.0.0'
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not found',
            'message': 'The requested resource was not found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
