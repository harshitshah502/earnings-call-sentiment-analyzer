import os
import requests
from dotenv import load_dotenv

load_dotenv()

def fetch_transcript(symbol, quarter):
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        raise ValueError("ALPHA_VANTAGE_API_KEY is missing from .env")

    response = requests.get(
        "https://www.alphavantage.co/query",
        params={
            "function": "EARNINGS_CALL_TRANSCRIPT",
            "symbol": symbol,
            "quarter": quarter,
            "apikey": api_key,
        },
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()
    transcript = data.get("transcript", [])

    return transcript
