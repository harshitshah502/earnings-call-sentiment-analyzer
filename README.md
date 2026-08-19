
# Real-Time Earnings Call & Sentiment Analyzer — Prototype

## What this project does
This prototype analyzes earnings-call text, assigns a sentiment score, classifies the call as Positive/Neutral/Negative, and combines the sentiment with simple financial indicators to generate a BUY/HOLD/SELL demonstration signal.

## Tech stack
- Python
- Pandas
- Streamlit
- Plotly
- Rule-based NLP sentiment scoring
- CSV dataset

## Folder structure
```
earnings_call_sentiment_analyzer/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   └── earnings_calls.csv
└── src/
    ├── __init__.py
    ├── preprocess.py
    └── sentiment.py
```

## Run locally
Open a terminal in this folder:

### Windows
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

### macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal.

## Google Colab
The dashboard is intended to run locally. The Python modules and CSV can also be imported in Colab for experiments.

## Algorithm
1. Load earnings-call records from CSV.
2. Normalize the text.
3. Tokenize the text into words.
4. Calculate a weighted sentiment score using positive/negative financial vocabulary.
5. Convert the score into Positive, Neutral, or Negative.
6. Combine sentiment with revenue growth and stock return to create a simple demonstration signal.
7. Visualize sentiment, returns, and company-level statistics.

## Important academic note
The BUY/HOLD/SELL output is a prototype research signal, not financial advice and not a production trading strategy. For a research paper, the next step should be to replace the rule-based sentiment engine with a trained transformer model and evaluate it with precision, recall, F1-score, and an out-of-sample backtest.

## Next upgrade
A production/live version can add:
- earnings-call API ingestion
- speech-to-text
- FinBERT/financial transformer sentiment
- real-time streaming
- database storage
- historical backtesting
- authentication
- cloud deployment
