
import re

POSITIVE = {
    "strong": 1.5, "growth": 1.2, "grew": 1.2, "healthy": 1.0,
    "accelerated": 1.5, "record": 1.5, "exceptional": 2.0,
    "improved": 1.2, "increase": 1.0, "increased": 1.0,
    "solid": 0.8, "confident": 1.0, "opportunities": 1.0,
    "demand": 0.3, "perform": 0.5, "performed": 0.7
}
NEGATIVE = {
    "below": -1.5, "declined": -1.8, "decline": -1.5,
    "pressure": -1.2, "constraints": -1.2, "cautious": -0.8,
    "softened": -1.0, "costs": -0.7, "uncertainty": -1.2,
    "restrictions": -1.0, "negative": -1.5, "slowed": -1.2
}

def score_text(text):
    words = re.findall(r"[a-z]+", str(text).lower())
    score = sum(POSITIVE.get(w, 0) for w in words) + sum(NEGATIVE.get(w, 0) for w in words)
    return score

def classify(score):
    if score >= 1.5:
        return "Positive"
    if score <= -1.0:
        return "Negative"
    return "Neutral"

def analyze(df):
    out = df.copy()
    out["sentiment_score"] = out["call_text"].apply(score_text)
    out["predicted_sentiment"] = out["sentiment_score"].apply(classify)
    # A simple academic signal combining sentiment and reported financial momentum.
    out["signal_score"] = (
        out["sentiment_score"] * 0.6 +
        out["revenue_growth_pct"] * 0.08 +
        out["stock_return_pct"] * 0.06
    )
    out["market_signal"] = out["signal_score"].apply(
        lambda x: "BUY" if x >= 1.5 else ("SELL" if x <= -1.0 else "HOLD")
    )
    return out
