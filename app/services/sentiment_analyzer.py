from .preprocessing import TextProcessor
import pickle
from pathlib import Path

class SentimentAnalyzer:
    def __init__(self):
        self.model = self.load_model()
        self.text_processor = TextProcessor()

    def load_model(self):
        """Load the vectorizer from the pickle file"""
        # Get the project root directory (2 levels up from current file)
        project_root = Path(__file__).parent.parent.parent
        model_path = project_root / "data" / "models" / "kindle_sentiment_analysis_model.pkl"
        
        try:
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
                print(f"Model loaded successfully from {model_path}")
                return model
        except FileNotFoundError:
            print(f"Model file not found at {model_path}")
            raise
        except Exception as e:
            print(f"Failed to load model: {e}")
            raise

    def analyze_sentiment(self, text):
        """Analyze sentiment of text and return binary classification (0=negative, 1=positive)"""
        try:
            # Preprocess the text
            processed_text = self.text_processor.preprocess(text)
            
            # Vectorize the processed text
            vectorized_text = self.text_processor.vectorize([processed_text])
            
            # Convert sparse matrix to dense array if needed
            if hasattr(vectorized_text, 'toarray'):
                vectorized_text = vectorized_text.toarray()
            
            # Get prediction (should be 0 or 1)
            prediction = self.model.predict(vectorized_text)
            
            # Ensure we return an integer (0 or 1)
            sentiment = int(prediction[0])
            
            # Validate the output is binary
            if sentiment not in [0, 1]:
                raise ValueError(f"Model returned unexpected value: {sentiment}. Expected 0 or 1.")
            
            return sentiment
            
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            raise
