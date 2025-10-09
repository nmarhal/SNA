import vaderSentiment.vaderSentiment as vader
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "model", "data")


def get_sentiment(line: str) -> dict[str, float]:
    analyzer = vader.SentimentIntensityAnalyzer()
    return analyzer.polarity_scores(line)
