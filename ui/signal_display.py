import streamlit as st
import pandas as pd

def display_signals_table(signals_df: pd.DataFrame, timeframes: list):
    st.subheader("Tickers with Breakout Signals:")
    st.dataframe(signals_df)
    all_tickers = [""] + signals_df['Ticker'].tolist()
    selected_ticker = st.selectbox("Select a ticker to view its chart:", all_tickers)
    selected_timeframe = None
    if selected_ticker:
        timeframe_options = [""] + timeframes
        selected_timeframe = st.selectbox("Select a timeframe for the chart:", timeframe_options)
        if selected_timeframe:
            return (selected_ticker, selected_timeframe)
    return (None, None)