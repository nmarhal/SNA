import vaderSentiment.vaderSentiment as vader
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "model", "data")


def get_sentiment(line: str) -> dict[str, float]:
    analyzer = vader.SentimentIntensityAnalyzer()
    return analyzer.polarity_scores(line)

def get_targeted_sentiment(line: str, target: str) -> dict[str, float]:
    doc = nlp(line)
    # Find spans mentioning the target (very simple alias match)
    spans = [ent for ent in doc.noun_chunks if ent.text.lower() in target_aliases]
    if not spans:
        return {"compound": None, "pos": 0.0, "neu": 1.0, "neg": 0.0}  # no target here

    # Extract a local window: governing clause of each mention
    texts = []
    for span in spans:
        head = span.root
        clause_tokens = {t for t in head.subtree}
        clause_text = " ".join(t.text for t in sorted(clause_tokens, key=lambda t: t.i))
        texts.append(clause_text)

    scores = [ANALYZER.polarity_scores(t)["compound"] for t in texts]
    compound = sum(scores) / len(scores)
    # derive bins for presentation
    if compound is None:
        label = "no-target"
    elif compound >= 0.4:
        label = "very positive"
    elif compound >= 0.1:
        label = "slightly positive"
    elif compound <= -0.4:
        label = "very negative"
    elif compound <= -0.1:
        label = "slightly negative"
    else:
        label = "neutral"
    return {"compound": compound, "label": label}