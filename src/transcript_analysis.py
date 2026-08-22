from src.transcript import fetch_transcript
from src.finbert import analyze_text


def transcript_summary(symbol, quarter):
    rows = fetch_transcript(symbol, quarter)

    if not rows:
        return None

    text = "\n\n".join(
        f"{r.get('speaker', 'Unknown')}: {r.get('content', '')}"
        for r in rows
    )

    chunks = [text[i:i+3500] for i in range(0, len(text), 3500)]

    results = []

    for chunk in chunks:
        results.append(analyze_text(chunk))

    scores = []

    for result in results:
        if result["label"] == "positive":
            scores.append(result["score"])
        elif result["label"] == "negative":
            scores.append(-result["score"])
        else:
            scores.append(0)

    average_score = sum(scores) / len(scores)

    if average_score > 0.15:
        label = "Positive"
    elif average_score < -0.15:
        label = "Negative"
    else:
        label = "Neutral"

    return {
        "entries": len(rows),
        "text": text,
        "average_sentiment": average_score,
        "label": label,
        "chunks_analyzed": len(chunks),
    }	