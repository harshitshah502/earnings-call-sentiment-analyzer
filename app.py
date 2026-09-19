import streamlit as st
import plotly.graph_objects as go
from src.company_resolver import resolve_company
from src.market_data import fetch_company_data
from src.analysis import build_snapshot
from src.transcript_analysis import transcript_summary

st.set_page_config(page_title="Earnings Intelligence", page_icon="📈", layout="wide")

st.markdown("""
<style>
.stApp{background:radial-gradient(circle at 85% 5%,rgba(124,92,255,.14),transparent 28%),radial-gradient(circle at 10% 80%,rgba(53,167,255,.08),transparent 25%),#070b14;color:#f5f7fb}
[data-testid="stSidebar"]{background:#080d17;border-right:1px solid #1d2a3d}
.block-container{max-width:1500px;padding-top:1.4rem}
h1,h2,h3{color:#f5f7fb!important}
[data-testid="stMetric"]{background:linear-gradient(145deg,#111a2b,#0b111d);border:1px solid #1d2a3d;border-radius:16px;padding:15px;box-shadow:0 10px 30px rgba(0,0,0,.2)}
[data-testid="stMetricLabel"]{color:#8d9ab0!important}
[data-testid="stMetricValue"]{color:#f5f7fb!important}
div[data-baseweb="input"]{background:#0d1422;border-radius:12px}
.stButton>button,.stFormSubmitButton>button{border-radius:11px;border:1px solid #31527b;background:linear-gradient(135deg,#1769aa,#6251e8);color:white;font-weight:700}
.stButton>button:hover,.stFormSubmitButton>button:hover{box-shadow:0 0 22px rgba(53,167,255,.2)}
.hero{background:radial-gradient(circle at 95% 10%,rgba(124,92,255,.2),transparent 30%),linear-gradient(145deg,#111a2c,#0a101c);border:1px solid #22334c;border-radius:22px;padding:24px 28px;margin:8px 0 20px}
.hero-title{font-size:2rem;font-weight:800}.hero-sub{color:#8d9ab0}.pill{display:inline-block;padding:5px 10px;border-radius:999px;background:rgba(53,167,255,.1);border:1px solid rgba(53,167,255,.25);color:#68beff;font-size:.78rem;font-weight:700}
.insight{background:rgba(124,92,255,.08);border:1px solid rgba(124,92,255,.22);border-radius:14px;padding:15px;color:#d9d5ff}
.footer{color:#66758d;font-size:.78rem;text-align:center;padding:25px}
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 🔷 Earnings Intelligence")
    st.caption("AI-Powered Market Intelligence")
    st.divider()
    st.markdown("### Navigation")
    st.markdown("🏠 **Dashboard**")
    st.markdown("🏢 Company Analysis")
    st.markdown("🎙️ Earnings Call")
    st.markdown("📊 Financials")
    st.markdown("🧠 AI Analysis")
    st.divider()
    st.caption("Real-time financial data + FinBERT")
    st.caption("Research / educational prototype")

st.markdown('<div class="hero"><div class="hero-title">📈 Earnings Intelligence</div><div class="hero-sub">Real-time financial analysis powered by market data, earnings transcripts and AI sentiment.</div></div>', unsafe_allow_html=True)

with st.form("company_search"):
    c1,c2=st.columns([5,1])
    with c1:
        query=st.text_input("Search company",placeholder="Try Apple, Microsoft, Tesla, NVIDIA, Amazon...",label_visibility="collapsed")
    with c2:
        submitted=st.form_submit_button("🔎 Analyze",type="primary",use_container_width=True)

if submitted:
    if not query.strip():
        st.warning("Enter a company name or ticker.")
        st.stop()
    with st.spinner(f"Analyzing {query.strip()}..."):
        try:
            company=resolve_company(query.strip())
            data=fetch_company_data(company["ticker"])
            snapshot=build_snapshot(company,data)
        except Exception as exc:
            st.error("We could not retrieve this company right now.")
            st.exception(exc)
            st.stop()
    st.session_state.update(company=company,data=data,snapshot=snapshot)

if "company" not in st.session_state:
    st.info("Search for a public company to begin.")
    st.markdown("### What happens next")
    st.markdown("**Company → Live market data → Earnings transcript → FinBERT → AI analysis → Dashboard**")
    st.stop()

company=st.session_state["company"]
data=st.session_state["data"]
snapshot=st.session_state["snapshot"]

st.markdown(f'<div class="hero"><span class="pill">{company["ticker"]}</span><div class="hero-title">{company["name"]}</div><div class="hero-sub">{company.get("exchange") or "Public market"} • Yahoo Finance • Live financial snapshot</div></div>',unsafe_allow_html=True)

c1,c2,c3,c4,c5=st.columns(5)
c1.metric("Current Price",f'{snapshot["current_price"]:,.2f}' if snapshot["current_price"] is not None else "N/A",f'{snapshot["change_pct"]:+.2f}%' if snapshot["change_pct"] is not None else None)
c2.metric("Market Cap",snapshot["market_cap_display"])
c3.metric("52W Change",f'{snapshot["52w_change"]:+.2f}%' if snapshot["52w_change"] is not None else "N/A")
c4.metric("P/E",snapshot["pe_display"])
c5.metric("Data Fields",len(data["available_fields"]))

st.markdown("### 📊 Market Performance")
period=st.radio("Time period",["1M","3M","6M","1Y","5Y"],horizontal=True,index=2)
period_map={"1M":"1mo","3M":"3mo","6M":"6mo","1Y":"1y","5Y":"5y"}
history=data["ticker"].history(period=period_map[period],auto_adjust=True)
if history is not None and not history.empty:
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=history.index,y=history["Close"],mode="lines",name="Close",line=dict(width=2.5)))
    fig.update_layout(height=390,margin=dict(l=10,r=10,t=15,b=10),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(color="#aeb8c8"),xaxis=dict(showgrid=False),yaxis=dict(gridcolor="#182437"),hovermode="x unified")
    st.plotly_chart(fig,use_container_width=True)
else:
    st.warning("Historical price data is unavailable for this period.")

left,right=st.columns([1,1])
with left:
    st.markdown("### 🏢 Company Snapshot")
    st.markdown(f'<div class="insight"><b>Industry:</b> {data["info"].get("industry") or "N/A"}<br><b>Sector:</b> {data["info"].get("sector") or "N/A"}<br><b>Employees:</b> {snapshot["employees_display"]}<br><b>Currency:</b> {data["info"].get("currency") or "N/A"}<br><br><b>Revenue:</b> {snapshot["revenue_display"]}<br><b>Profit Margin:</b> {snapshot["profit_margin_display"]}<br><b>P/E:</b> {snapshot["pe_display"]}</div>',unsafe_allow_html=True)

with right:
    st.markdown("### 🤖 Automatic AI Analysis")
    a,b,c=st.columns(3)
    a.metric("Momentum",snapshot["momentum_label"])
    b.metric("52W Position",snapshot["range_label"])
    c.metric("Data Quality",snapshot["data_quality"])
    st.info(snapshot["interpretation"])

st.markdown("### 💰 Quarterly Financials")
if not data["financials"].empty:
    st.dataframe(data["financials"],use_container_width=True)
else:
    st.info("Detailed quarterly financial statement data was unavailable.")

st.markdown("### 🧾 Earnings Information")
if not data["earnings"].empty:
    st.dataframe(data["earnings"],use_container_width=True)
else:
    st.info("Recent earnings-date information was unavailable.")

st.markdown("### 🎙️ Earnings Call AI Analysis")
quarter=st.text_input("Earnings quarter (YYYYQM)",value="2025Q4")
if st.button("🧠 Analyze Earnings Call",type="primary"):
    with st.spinner("Retrieving transcript and running FinBERT..."):
        try:
            ts=transcript_summary(company["ticker"],quarter)
            if ts is None:
                st.warning("No transcript available for this quarter.")
            else:
                c1,c2,c3=st.columns(3)
                c1.metric("Transcript Entries",ts["entries"])
                c2.metric("AI Sentiment",ts["label"])
                c3.metric("Sentiment Score",f'{ts["average_sentiment"]:.3f}')
                if ts["label"]=="Positive":
                    st.success("Management sentiment is predominantly positive.")
                elif ts["label"]=="Negative":
                    st.error("Management sentiment is predominantly negative.")
                else:
                    st.info("Management sentiment is relatively neutral.")
                with st.expander("📄 View Earnings Transcript"):
                    st.write(ts["text"])
        except Exception as exc:
            st.error("Could not retrieve the transcript.")
            st.exception(exc)

with st.expander("🔧 Technical Details"):
    st.write("Ticker:",company["ticker"])
    st.write("Resolver:",company.get("resolver"))
    st.write("Retrieved fields:",", ".join(sorted(data["available_fields"])))



# =============================
# AI Syllabus Lab
# =============================
st.markdown("## 🧠 AI Syllabus Lab")
st.caption("Algorithms from the AI course are applied to the live company analysis pipeline.")

try:
    from src.syllabus_ai import run_syllabus_suite
    transcript_score = float(st.session_state.get("transcript_score", 0.0))
    if st.button("⚙️ Run AI Syllabus Analysis", type="primary"):
        with st.spinner("Running Decision Tree, K-Means, search, optimization and reasoning algorithms..."):
            suite = run_syllabus_suite(history, transcript_score)
        st.session_state["ai_suite"] = suite
except Exception as exc:
    st.warning("AI syllabus module is not ready yet.")
    st.caption(str(exc))

if "ai_suite" in st.session_state:
    suite = st.session_state["ai_suite"]
    tabs = st.tabs(["🌳 ML", "🔵 K-Means", "🔎 Search", "🧬 Optimization", "🎮 Adversarial", "🧠 Logic & CSP"])

    with tabs[0]:
        st.markdown("### Decision Tree")
        tree = suite["decision_tree"]
        if tree:
            a,b,c,d = st.columns(4)
            a.metric("Prediction", tree["prediction"])
            b.metric("Confidence", f'{tree["confidence"]*100:.1f}%')
            c.metric("Test Accuracy", f'{tree["accuracy"]*100:.1f}%')
            d.metric("Tree Depth", tree["depth"])
            st.dataframe(tree["importance"], use_container_width=True, hide_index=True)
            st.caption("The tree is trained on historical price-derived features and classifies the next 20-day return regime.")
        else:
            st.info("Not enough historical data to train the Decision Tree.")

    with tabs[1]:
        st.markdown("### K-Means Market Regimes")
        km = suite["kmeans"]
        if km:
            a,b = st.columns(2)
            a.metric("Current Cluster", km["cluster"])
            b.metric("Silhouette Score", f'{km["silhouette"]:.3f}')
            st.success(f'Current regime: **{km["regime"]}**')
            kdata = km["data"].copy()
            kdata["Cluster"] = km["labels"]
            st.dataframe(kdata.tail(25), use_container_width=True, hide_index=True)
            st.caption("K-Means groups historical market windows by return, momentum and volatility.")
        else:
            st.info("Not enough historical data for clustering.")

    with tabs[2]:
        st.markdown("### Search Algorithms")
        st.caption("Graph search over the project's financial-analysis dependency graph.")
        for name, result in suite["search"].items():
            if isinstance(result, tuple):
                path, cost = result
                st.write(f"**{name}:** {' → '.join(path)}  | cost = {cost}")
            else:
                st.write(f"**{name}:** {' → '.join(result)}")

    with tabs[3]:
        st.markdown("### Optimization Algorithms")
        a,b = st.columns(2)
        a.metric("Hill Climbing optimum", suite["optimization"]["Hill Climbing optimum"])
        b.metric("Genetic Algorithm optimum", suite["optimization"]["Genetic Algorithm optimum"])
        st.caption("Small deterministic optimization demonstrations mapped into the AI analysis lab.")

    with tabs[4]:
        st.markdown("### Adversarial Search")
        a,b = st.columns(2)
        a.metric("Minimax", suite["adversarial"]["Minimax"])
        b.metric("Alpha-Beta", suite["adversarial"]["Alpha-Beta"])
        st.caption("Minimax and Alpha-Beta pruning are implemented as adversarial-search demonstrations.")

    with tabs[5]:
        st.markdown("### Knowledge Representation & Reasoning")
        logic = suite["logic"]
        st.write("**Initial facts:**", ", ".join(logic["facts"]))
        st.write("**Forward-chained facts:**", ", ".join(logic["derived"]))
        st.write("**Backward chaining:**", "Goal proved" if logic["backward_chaining_positive_state"] else "Goal not proved")
        st.markdown("### CSP")
        st.json(suite["csp"])
        st.caption("Forward chaining, backward chaining and a constraint-satisfaction demonstration are included in the project.")

st.markdown('<div class="footer">Earnings Intelligence • Research / educational prototype • Data availability and freshness can vary. Not investment advice.</div>',unsafe_allow_html=True)
