import streamlit as st
import plotly.graph_objects as go
from src.company_resolver import resolve_company
from src.market_data import fetch_company_data
from src.analysis import build_snapshot

st.set_page_config(page_title="Earnings Intelligence", page_icon="📈", layout="wide")
st.title("📈 Earnings Intelligence")
st.caption("Version 2.0 — automatic company lookup and live market/financial data")

with st.form("company_search"):
    query = st.text_input("Search for a company", placeholder="Try Apple, Microsoft, Tesla, NVIDIA, Amazon...")
    submitted = st.form_submit_button("🔎 Analyze company", type="primary")

if submitted:
    if not query.strip():
        st.warning("Enter a company name or ticker.")
        st.stop()
    with st.spinner(f"Finding and analyzing {query.strip()}..."):
        try:
            company = resolve_company(query.strip())
            data = fetch_company_data(company["ticker"])
            snapshot = build_snapshot(company, data)
        except Exception as exc:
            st.error("We could not retrieve this company right now.")
            st.exception(exc)
            st.stop()
    st.session_state.update(company=company, data=data, snapshot=snapshot)

if "company" not in st.session_state:
    st.info("Search for a public company to begin. No CSV upload is required in Version 2.0.")
    st.markdown("### What Version 2.0 does\n**Company name → ticker → live data → automatic analysis → dashboard**")
    st.stop()

company = st.session_state["company"]
data = st.session_state["data"]
snapshot = st.session_state["snapshot"]

st.subheader(f"{company['name']} ({company['ticker']})")
st.caption(f"{company.get('exchange') or 'Public market'} • Data source: Yahoo Finance via yfinance")

c1,c2,c3,c4 = st.columns(4)
c1.metric("Current price", f"{snapshot['current_price']:,.2f}" if snapshot["current_price"] is not None else "N/A",
          f"{snapshot['change_pct']:+.2f}%" if snapshot["change_pct"] is not None else None)
c2.metric("Market cap", snapshot["market_cap_display"])
c3.metric("52-week change", f"{snapshot['52w_change']:+.2f}%" if snapshot["52w_change"] is not None else "N/A")
c4.metric("Data sources", len(data["available_fields"]))

st.divider()
st.subheader("📊 Price performance")
period = st.radio("Period", ["1M","3M","6M","1Y","5Y"], horizontal=True, index=2)
period_map={"1M":"1mo","3M":"3mo","6M":"6mo","1Y":"1y","5Y":"5y"}
history=data["ticker"].history(period=period_map[period], auto_adjust=True)
if history is not None and not history.empty:
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=history.index,y=history["Close"],mode="lines",name="Close"))
    fig.update_layout(height=420,margin=dict(l=10,r=10,t=20,b=10),xaxis_title="Date",yaxis_title="Price",hovermode="x unified")
    st.plotly_chart(fig,use_container_width=True)
else:
    st.warning("Historical price data is unavailable for this period.")

st.subheader("🏢 Company snapshot")
left,right=st.columns(2)
with left:
    st.markdown(f"**Industry:** {data['info'].get('industry') or 'N/A'}")
    st.markdown(f"**Sector:** {data['info'].get('sector') or 'N/A'}")
    st.markdown(f"**Employees:** {snapshot['employees_display']}")
    st.markdown(f"**Currency:** {data['info'].get('currency') or 'N/A'}")
with right:
    st.markdown(f"**Revenue (latest):** {snapshot['revenue_display']}")
    st.markdown(f"**Profit margin:** {snapshot['profit_margin_display']}")
    st.markdown(f"**P/E:** {snapshot['pe_display']}")
    st.markdown(f"**Dividend yield:** {snapshot['dividend_display']}")

if data["info"].get("longBusinessSummary"):
    with st.expander("Company description"):
        st.write(data["info"]["longBusinessSummary"])

st.subheader("💰 Quarterly financials")
if not data["financials"].empty:
    st.dataframe(data["financials"],use_container_width=True)
else:
    st.info("Detailed quarterly financial statement data was unavailable.")

st.subheader("🧾 Earnings dates")
if not data["earnings"].empty:
    st.dataframe(data["earnings"],use_container_width=True)
else:
    st.info("Recent earnings-date information was unavailable.")

st.subheader("🤖 Automatic V2.0 analysis")
a,b,c=st.columns(3)
a.metric("Price momentum",snapshot["momentum_label"])
b.metric("52-week position",snapshot["range_label"])
c.metric("Data quality",snapshot["data_quality"])
st.info(snapshot["interpretation"])
st.caption("V2.0 is a research/educational data-retrieval prototype, not investment advice. Data availability and freshness can vary.")
with st.expander("🔧 Technical details"):
    st.write("Ticker:",company["ticker"])
    st.write("Resolver:",company.get("resolver"))
    st.write("Retrieved fields:",", ".join(sorted(data["available_fields"])))
