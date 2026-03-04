import sys
import json
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

def ensure_vader():
    try:
        nltk.data.find('sentiment/vader_lexicon.zip')
    except LookupError:
        # Download quietly
        nltk.download('vader_lexicon', quiet=True)

def analyze(text):
    ensure_vader()
    sia = SentimentIntensityAnalyzer()
    scores = sia.polarity_scores(text)
    return scores

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No text provided"}))
        sys.exit(1)

    text = " ".join(sys.argv[1:])
    try:
        scores = analyze(text)
        print(json.dumps(scores))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
