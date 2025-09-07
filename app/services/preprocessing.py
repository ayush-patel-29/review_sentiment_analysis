from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import pickle
import re
from pathlib import Path

class TextProcessor:
    def __init__(self, language='english'):
        self.stop_words = set(stopwords.words(language))
        self.lemmatizer = WordNetLemmatizer()
        self.vectorizer = None
        self.load_vectorizer()

    def preprocess(self, text):
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation and special characters
        text =  re.sub('[^a-z A-Z 0-9]+',' ',text)
        
        # Tokenize and remove stop words
        tokens = text.split()
        filtered_tokens = [word for word in tokens if word not in self.stop_words]
        
        # Removes URL
        filtered_tokens = [re.sub(r'\b(?:[a-z][a-z0-9+\-.]*):\/\/(?:[\w\-]+\.)+[a-z]{2,}(?:\/[^\s]*)?\b', ' ', word, flags=re.MULTILINE) for word in filtered_tokens]
        
        # Removes Unwanted spaces and join tokens
        filtered_tokens = " ".join(filtered_tokens).split()
    
        # Lemmatization
        lemmatized_tokens = [self.lemmatizer.lemmatize(word) for word in filtered_tokens]
        
        return ' '.join(lemmatized_tokens)
    
    def load_vectorizer(self):
        """Load the vectorizer from the pickle file"""
        # Get the project root directory (2 levels up from current file)
        project_root = Path(__file__).parent.parent.parent
        vectorizer_path = project_root / "data" / "models" / "vectorizer.pkl"
        
        try:
            with open(vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            print(f"Vectorizer loaded successfully from {vectorizer_path}")
        except FileNotFoundError:
            print(f"Vectorizer file not found at {vectorizer_path}")
            raise
        except Exception as e:
            print(f"Error loading vectorizer: {e}")
            raise
    
    def vectorize(self, texts):
        """Transform texts using the loaded vectorizer"""
        if self.vectorizer is None:
            raise ValueError("Vectorizer not loaded. Call load_vectorizer() first.")
        
        # Handle both single text and list of texts
        if isinstance(texts, str):
            texts = [texts]
            
        return self.vectorizer.transform(texts)
