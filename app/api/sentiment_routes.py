from flask import Blueprint, request, jsonify, current_app
import logging
from typing import Dict, List, Any

sentiment_bp = Blueprint('sentiment', __name__)


def validate_text_input(data: Dict) -> tuple[bool, str]:
    """Validate text input from request"""
    if not data:
        return False, "Request body cannot be empty"
    
    if 'text' not in data:
        return False, "Missing 'text' field in request body"
    
    text = data.get('text', '').strip()
    if not text:
        return False, "Text field cannot be empty"
    
    if len(text) > 5000:  # Set reasonable limit
        return False, "Text too long. Maximum 5000 characters allowed"
    
    return True, ""


def validate_batch_input(data: Dict) -> tuple[bool, str]:
    """Validate batch input from request"""
    if not data:
        return False, "Request body cannot be empty"
    
    if 'texts' not in data:
        return False, "Missing 'texts' field in request body"
    
    texts = data.get('texts', [])
    if not isinstance(texts, list):
        return False, "'texts' must be a list"
    
    if not texts:
        return False, "Texts list cannot be empty"
    
    if len(texts) > 100:  # Set reasonable batch limit
        return False, "Too many texts. Maximum 100 texts allowed per batch"
    
    for i, text in enumerate(texts):
        if not isinstance(text, str):
            return False, f"Text at index {i} must be a string"
        
        if not text.strip():
            return False, f"Text at index {i} cannot be empty"
        
        if len(text) > 5000:
            return False, f"Text at index {i} too long. Maximum 5000 characters allowed"
    
    return True, ""


@sentiment_bp.route('/sentiment/analyze', methods=['POST'])
def analyze_sentiment():
    """
    Analyze sentiment of a single text
    
    Expected JSON payload:
    {
        "text": "Your review text here"
    }
    
    Returns:
    {
        "sentiment": "positive|negative",
        "text": "original text",
        "processed": true
    }
    """
    try:
        data = request.get_json()
        
        # Validate input
        is_valid, error_msg = validate_text_input(data)
        if not is_valid:
            return jsonify({
                'error': 'Validation error',
                'message': error_msg
            }), 400
        
        text = data['text']
        
        # Get sentiment analyzer from app context
        analyzer = current_app.sentiment_analyzer
        
        # Analyze sentiment
        sentiment = analyzer.analyze_sentiment(text)
        
        # Map numeric sentiment to readable labels (adjust based on your model)
        sentiment_labels = {0: 'negative', 1: 'positive'}
        sentiment_label = sentiment_labels.get(sentiment, 'unknown')
        
        return jsonify({
            'sentiment': sentiment_label,
            'text': text,
            'processed': True,
            'raw_prediction': int(sentiment)
        })
    
    except Exception as e:
        current_app.logger.error(f"Error in sentiment analysis: {str(e)}")
        return jsonify({
            'error': 'Analysis failed',
            'message': 'Failed to analyze sentiment'
        }), 500


@sentiment_bp.route('/sentiment/analyze/batch', methods=['POST'])
def analyze_sentiment_batch():
    """
    Analyze sentiment of multiple texts
    
    Expected JSON payload:
    {
        "texts": ["Review 1", "Review 2", "Review 3"]
    }
    
    Returns:
    {
        "results": [
            {
                "text": "Review 1",
                "sentiment": "positive",
                "raw_prediction": 1
            },
            ...
        ],
        "processed_count": 3,
        "success": true
    }
    """
    try:
        data = request.get_json()
        
        # Validate input
        is_valid, error_msg = validate_batch_input(data)
        if not is_valid:
            return jsonify({
                'error': 'Validation error',
                'message': error_msg
            }), 400
        
        texts = data['texts']
        
        # Get sentiment analyzer from app context
        analyzer = current_app.sentiment_analyzer
        
        results = []
        sentiment_labels = {0: 'negative', 1: 'positive'}
        
        # Process each text
        for text in texts:
            try:
                sentiment = analyzer.analyze_sentiment(text)
                sentiment_label = sentiment_labels.get(sentiment, 'unknown')
                
                results.append({
                    'text': text,
                    'sentiment': sentiment_label,
                    'raw_prediction': int(sentiment)
                })
            except Exception as e:
                current_app.logger.error(f"Error analyzing text '{text[:50]}...': {str(e)}")
                results.append({
                    'text': text,
                    'sentiment': 'error',
                    'error': 'Analysis failed'
                })
        
        return jsonify({
            'results': results,
            'processed_count': len(results),
            'success': True
        })
    
    except Exception as e:
        current_app.logger.error(f"Error in batch sentiment analysis: {str(e)}")
        return jsonify({
            'error': 'Batch analysis failed',
            'message': 'Failed to analyze sentiments'
        }), 500


@sentiment_bp.route('/sentiment/info', methods=['GET'])
def sentiment_info():
    """
    Get information about the sentiment analysis service
    
    Returns:
    {
        "service": "sentiment_analysis",
        "model_loaded": true,
        "supported_sentiments": ["positive", "negative"],
        "limits": {
            "max_text_length": 5000,
            "max_batch_size": 100
        }
    }
    """
    try:
        model_loaded = hasattr(current_app, 'sentiment_analyzer') and current_app.sentiment_analyzer is not None
        
        return jsonify({
            'service': 'sentiment_analysis',
            'model_loaded': model_loaded,
            'supported_sentiments': ['positive', 'negative'],
            'limits': {
                'max_text_length': 5000,
                'max_batch_size': 100
            },
            'endpoints': {
                'single_analysis': '/api/v1/sentiment/analyze',
                'batch_analysis': '/api/v1/sentiment/analyze/batch',
                'service_info': '/api/v1/sentiment/info'
            }
        })
    
    except Exception as e:
        current_app.logger.error(f"Error getting sentiment info: {str(e)}")
        return jsonify({
            'error': 'Info retrieval failed',
            'message': 'Failed to get service information'
        }), 500
