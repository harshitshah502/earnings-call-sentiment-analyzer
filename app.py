
import streamlit as st
import pandas as pd
import plotly.express as px
from src.preprocess import load_data
from src.sentiment import analyze

st.set_page_config(page_title="Earnings Call Sentiment Analyzer", page_icon="📈", layout="wide")

st.title("📈 Real-Time Earnings Call & Sentiment Analyzer")
st.caption("Academic prototype — local earnings-call dataset with sentiment and market-signal analysis.")

df = load_data()
result = analyze(df)

with st.sidebar:
    st.header("Filters")
    companies = st.multiselect("Company", sorted(result.company.unique()), default=sorted(result.company.unique()))
    sentiments = st.multiselect("Predicted Sentiment", ["Positive","Neutral","Negative"], default=["Positive","Neutral","Negative"])

filtered = result[result.company.isin(companies) & result.predicted_sentiment.isin(sentiments)].copy()

c1,c2,c3,c4 = st.columns(4)
c1.metric("Calls analyzed", len(filtered))
c2.metric("Positive calls", int((filtered.predicted_sentiment=="Positive").sum()))
c3.metric("Negative calls", int((filtered.predicted_sentiment=="Negative").sum()))
c4.metric("Avg stock return", f"{filtered.stock_return_pct.mean():.2f}%" if len(filtered) else "0%")

st.subheader("Sentiment distribution")
if len(filtered):
    fig = px.bar(filtered["predicted_sentiment"].value_counts().rename_axis("Sentiment").reset_index(name="Calls"),
                 x="Sentiment", y="Calls", title="Predicted sentiment")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Sentiment vs. stock return")
    fig2 = px.scatter(filtered, x="sentiment_score", y="stock_return_pct",
                      color="predicted_sentiment", hover_name="company",
                      hover_data=["quarter","revenue_growth_pct","market_signal"],
                      title="Sentiment score vs. stock return")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Company analysis")
    company_summary = filtered.groupby("company").agg(
        calls=("company","size"),
        avg_sentiment=("sentiment_score","mean"),
        avg_revenue_growth=("revenue_growth_pct","mean"),
        avg_stock_return=("stock_return_pct","mean")
    ).reset_index()
    st.dataframe(company_summary, use_container_width=True)

    st.subheader("Call-level results")
    st.dataframe(filtered[["company","quarter","call_text","predicted_sentiment","sentiment_score",
                            "revenue_growth_pct","stock_return_pct","market_signal"]], use_container_width=True)
else:
    st.warning("Select at least one company and sentiment.")
