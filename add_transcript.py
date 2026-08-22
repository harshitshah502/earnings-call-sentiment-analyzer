from src.transcript_analysis import transcript_summary

st.divider()
st.subheader('🎙️ Earnings Call Analysis')

quarter = st.text_input('Earnings quarter (YYYYQM)', value='2025Q4')

if st.button('Analyze earnings call'):
    with st.spinner('Retrieving earnings transcript...'):
        try:
            ts = transcript_summary(company['ticker'], quarter)

            if ts is None:
                st.warning('No transcript available for this quarter.')
            else:
                c1, c2, c3 = st.columns(3)

                c1.metric('Transcript entries', ts['entries'])
                c2.metric('AI sentiment', ts['label'])
                c3.metric('Sentiment score', f"{ts['average_sentiment']:.3f}")

                if ts['label'] == 'Positive':
                    st.success('Management sentiment is predominantly positive.')
                elif ts['label'] == 'Negative':
                    st.error('Management sentiment is predominantly negative.')
                else:
                    st.info('Management sentiment is relatively neutral.')

                with st.expander('View earnings transcript'):
                    st.write(ts['text'])

        except Exception as exc:
            st.error('Could not retrieve the transcript.')
            st.exception(exc)