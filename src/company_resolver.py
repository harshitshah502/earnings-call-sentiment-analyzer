import re
import yfinance as yf

ALIASES={
"apple":"AAPL","microsoft":"MSFT","amazon":"AMZN","amazon.com":"AMZN",
"google":"GOOGL","alphabet":"GOOGL","nvidia":"NVDA","tesla":"TSLA",
"meta":"META","facebook":"META","netflix":"NFLX","berkshire hathaway":"BRK-B",
"jpmorgan":"JPM","jp morgan":"JPM","walmart":"WMT","visa":"V","mastercard":"MA"
}

def resolve_company(query):
    raw=re.sub(r"\s+"," ",str(query).strip())
    key=raw.lower()
    fallback=ALIASES.get(key,raw.upper())

    if key not in ALIASES and re.fullmatch(r"[A-Za-z.\-]{1,7}",raw):
        try:
            t=yf.Ticker(raw.upper())
            h=t.history(period="5d",auto_adjust=False)
            if h is not None and not h.empty:
                info=t.info or {}
                return {"ticker":raw.upper(),"name":info.get("longName") or info.get("shortName") or raw.upper(),
                        "exchange":info.get("exchange"),"resolver":"ticker validation"}
        except Exception: pass

    try:
        results=yf.Search(raw).quotes
    except Exception:
        results=[]
    candidates=[q for q in results if q.get("symbol") and q.get("quoteType") in (None,"EQUITY","ETF")]
    if candidates:
        q=candidates[0]
        return {"ticker":q["symbol"],"name":q.get("longname") or q.get("shortname") or q["symbol"],
                "exchange":q.get("exchange"),"resolver":"Yahoo Finance search"}

    try:
        t=yf.Ticker(fallback); h=t.history(period="5d",auto_adjust=False)
        if h is None or h.empty: raise ValueError
        info=t.info or {}
        return {"ticker":fallback,"name":info.get("longName") or info.get("shortName") or fallback,
                "exchange":info.get("exchange"),"resolver":"ticker fallback"}
    except Exception as exc:
        raise ValueError(f"Could not find a public company for '{query}'. Try a company name or ticker such as AAPL.") from exc
