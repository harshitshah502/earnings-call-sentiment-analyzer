import pandas as pd
import yfinance as yf

def _info(t):
    try: return t.info or {}
    except Exception: return {}

def _history(t):
    try: return t.history(period="5y",auto_adjust=True)
    except Exception: return pd.DataFrame()

def _financials(t):
    try:
        q=t.quarterly_income_stmt
        if q is None or q.empty: return pd.DataFrame()
        preferred=["Total Revenue","Operating Income","Net Income","Diluted EPS","Basic EPS"]
        rows=[r for r in preferred if r in q.index]
        out=q.loc[rows].copy() if rows else q.head(12).copy()
        out.columns=[str(c.date()) if hasattr(c,"date") else str(c) for c in out.columns]
        return out
    except Exception: return pd.DataFrame()

def _earnings(t):
    try:
        e=t.get_earnings_dates(limit=12)
        return e.reset_index() if e is not None else pd.DataFrame()
    except Exception: return pd.DataFrame()

def fetch_company_data(symbol):
    t=yf.Ticker(symbol); info=_info(t); history=_history(t); financials=_financials(t); earnings=_earnings(t)
    fields={"history"}
    if info: fields.add("company_info")
    if not financials.empty: fields.add("quarterly_financials")
    if not earnings.empty: fields.add("earnings_dates")
    return {"ticker":t,"info":info,"history":history,"financials":financials,"earnings":earnings,"available_fields":fields}
