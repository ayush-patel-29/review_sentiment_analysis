# Review Sentiment Analysis

A Flask web application for sentiment analysis of text reviews.

## Project Structure

```
review_sentiment_analysis/
├── app/
│   ├── api/
│   │   └── sentiment_routes.py
│   ├── services/
│   │   ├── preprocessing.py
│   │   └── sentiment_analyzer.py
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── app.js
│   ├── templates/
│   │   └── index.html
│   ├── utils/
│   │   └── error_handlers.py
│   └── main.py
├── data/
│   ├── models/
│   │   ├── kindle_sentiment_analysis_model.pkl
│   │   └── vectorizer.pkl
│   ├── notebook/
│   │   └── Kindle_Sentiment_Analysis.ipynb
│   └── sample/
│       └── all_kindle_review.csv
├── .gitignore
├── .python-version
├── pyproject.toml
├── README.md
└── uv.lock
```

## What it does

- Analyzes sentiment of text (positive/negative)
- Supports single text analysis and batch analysis
- Provides confidence scores
- Web interface with dark theme

## How to use

1. Clone the repository:
   ```
   git clone https://github.com/ayush-patel-29/review_sentiment_analysis
   cd review_sentiment_analysis
   ```

2. Install dependencies:
   ```
   uv sync
   ```

3. Run the application:
   ```
   python app/main.py
   ```

4. Open browser to `http://127.0.0.1:5000/`

5. Enter text for analysis or use batch mode for multiple texts

## API Endpoints

- `POST /api/sentiment` - Single text analysis
- `POST /api/sentiment/batch` - Batch text analysis
