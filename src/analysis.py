import math

def _num(v):
    try:
        x=float(v)
        return x if math.isfinite(x) else None
    except Exception: return None

def _money(v):
    v=_num(v)
    if v is None:return "N/A"
    if abs(v)>=1e12:return f"${v/1e12:.2f}T"
    if abs(v)>=1e9:return f"${v/1e9:.2f}B"
    if abs(v)>=1e6:return f"${v/1e6:.2f}M"
    return f"${v:,.2f}"

def build_snapshot(company,data):
    info=data["info"]; hist=data["history"]
    current=previous=None
    if hist is not None and not hist.empty and "Close" in hist:
        c=hist["Close"].dropna()
        if not c.empty:
            current=_num(c.iloc[-1])
            if len(c)>=2: previous=_num(c.iloc[-2])
    change=None if current is None or previous in (None,0) else (current/previous-1)*100
    fifty=_num(info.get("52WeekChange"))
    if fifty is not None:fifty*=100
    cap=_num(info.get("marketCap")); rev=_num(info.get("totalRevenue"))
    margin=_num(info.get("profitMargins")); pe=_num(info.get("trailingPE")); div=_num(info.get("dividendYield"))
    emp=info.get("fullTimeEmployees")
    if fifty is not None: range_label=f"{fifty:+.1f}% vs year ago"
    else: range_label="N/A"
    momentum="Positive" if change is not None and change>=1 else "Negative" if change is not None and change<=-1 else "Flat" if change is not None else "Unavailable"
    quality="High" if len(data["available_fields"])>=4 else "Good" if len(data["available_fields"])>=2 else "Basic"
    if change is None: interpretation="Market price data was retrieved, but a short-term comparison was unavailable."
    elif change>1: interpretation=f"{company['name']} shows positive short-term price momentum ({change:+.2f}% versus the previous available session). This is descriptive analysis, not a recommendation."
    elif change<-1: interpretation=f"{company['name']} shows negative short-term price momentum ({change:+.2f}% versus the previous available session). This is descriptive analysis, not a recommendation."
    else: interpretation=f"{company['name']} shows relatively stable short-term price movement ({change:+.2f}% versus the previous available session)."
    return {"current_price":current,"change_pct":change,"market_cap_display":_money(cap),"52w_change":fifty,
            "range_label":range_label,"momentum_label":momentum,"data_quality":quality,
            "revenue_display":_money(rev),"profit_margin_display":f"{margin*100:.2f}%" if margin is not None else "N/A",
            "pe_display":f"{pe:.2f}" if pe is not None else "N/A",
            "dividend_display":f"{div*100:.2f}%" if div is not None else "N/A",
            "employees_display":f"{int(emp):,}" if isinstance(emp,(int,float)) else "N/A",
            "interpretation":interpretation}
