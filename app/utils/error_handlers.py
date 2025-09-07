from flask import jsonify, request, current_app
import traceback
import sys


def handle_validation_error(error_message: str, status_code: int = 400):
    """Handle validation errors with consistent format"""
    return jsonify({
        'error': 'Validation Error',
        'message': error_message,
        'status_code': status_code
    }), status_code


def handle_model_error(error_message: str = "Model processing failed"):
    """Handle model-related errors"""
    return jsonify({
        'error': 'Model Error',
        'message': error_message,
        'status_code': 500
    }), 500


def handle_generic_error(error: Exception, custom_message: str = None):
    """Handle generic exceptions with logging"""
    error_message = custom_message or "An unexpected error occurred"
    
    # Log the full error for debugging
    current_app.logger.error(f"Error processing request: {str(error)}")
    current_app.logger.error(f"Request URL: {request.url}")
    current_app.logger.error(f"Request method: {request.method}")
    
    # Log full traceback in debug mode
    if current_app.config.get('DEBUG'):
        current_app.logger.error(f"Full traceback: {traceback.format_exc()}")
    
    return jsonify({
        'error': 'Server Error',
        'message': error_message,
        'status_code': 500
    }), 500


def register_error_handlers(app):
    """Register global error handlers for the Flask app"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad Request',
            'message': 'The request was invalid or malformed',
            'status_code': 400
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found',
            'status_code': 404
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'error': 'Method Not Allowed',
            'message': f'Method {request.method} is not allowed for this endpoint',
            'status_code': 405
        }), 405
    
    @app.errorhandler(415)
    def unsupported_media_type(error):
        return jsonify({
            'error': 'Unsupported Media Type',
            'message': 'Content-Type must be application/json',
            'status_code': 415
        }), 415
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected server error occurred',
            'status_code': 500
        }), 500
    
    @app.before_request
    def log_request_info():
        """Log incoming requests for debugging"""
        if current_app.config.get('DEBUG'):
            current_app.logger.info(f"Request: {request.method} {request.url}")
            if request.is_json and request.get_json():
                # Don't log sensitive data, just the structure
                data = request.get_json()
                if isinstance(data, dict):
                    keys = list(data.keys())
                    current_app.logger.info(f"Request JSON keys: {keys}")
    
    @app.after_request
    def log_response_info(response):
        """Log outgoing responses for debugging"""
        if current_app.config.get('DEBUG'):
            current_app.logger.info(f"Response: {response.status_code}")
        return response
