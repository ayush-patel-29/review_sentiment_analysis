from preprocessing import TextProcessor
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
        processed_text = self.text_processor.preprocess(text)
        sentiment = self.model.predict([processed_text])
        return sentiment[0]