from transformers import pipeline

_model = None

def get_model():
    global _model

    if _model is None:
        _model = pipeline(
            "sentiment-analysis",
            model="ProsusAI/finbert"
        )

    return _model


def analyze_text(text):
    model = get_model()

    result = model(
        text[:4000],
        truncation=True
    )[0]

    return {
        "label": result["label"],
        "score": result["score"]
    }