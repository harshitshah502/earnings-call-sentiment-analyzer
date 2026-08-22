# Earnings Call Sentiment Analyzer — Version 2.0

V2.0 changes the workflow from a fixed CSV demo to automatic company lookup and live market/financial retrieval.

**Company name → ticker → live data → automatic analysis → dashboard**

Try Apple, Microsoft, Tesla, NVIDIA, Amazon, AAPL, MSFT or NVDA.

## Run on this PC

```powershell
$env:PYTHONPATH="D:\Lib\site-packages"
D:\python.exe -m pip install -r requirements.txt
D:\python.exe -m streamlit run app.py
```

V2.0 displays current price, short-term movement, market cap, 52-week performance, company information, revenue, margin, P/E, dividend yield, historical prices, quarterly financial rows and recent earnings dates.

## Data-source note

V2.0 uses yfinance, an open-source package that accesses publicly available Yahoo Finance data and is intended for research/educational use. It is not affiliated with Yahoo. A later production version should use licensed/official APIs where appropriate.

## Next versions

V2.1: earnings-call transcript retrieval
V2.2: FinBERT financial sentiment
V2.3: key topics, risks and outlook
V2.4: signal engine
V2.5: backtesting and evaluation
V3.0: live multi-source earnings intelligence dashboard
