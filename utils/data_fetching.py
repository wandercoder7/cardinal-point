import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

@st.cache_data
def fetch_stock_data(ticker, period="1y", interval="1d"):
    """
    Fetches historical stock data from Yahoo Finance.

    Args:
        ticker (str): Stock ticker symbol.
        period (str): Period for fetching data (e.g., '1y', '6mo').
        interval (str): Data interval (e.g., '1d', '1wk').

    Returns:
        pd.DataFrame: DataFrame containing the stock data.
    """
    try:
        data = yf.download(ticker, period=period, interval=interval)
        if data.empty:
            st.warning(f"No data found for {ticker}.")
            return None
        # Remove incomplete intervals
        now = datetime.now()
        if interval == "1d":
            # Remove today's data if the current time is before 4 PM
            market_close_time = now.replace(hour=15, minute=30, second=0, microsecond=0)
            if now < market_close_time and not data.index[-1].date() < now.date():
                data = data.iloc[:-1]
        elif interval == "1wk":
            # Remove the current week's data if today is not Monday
            if now.weekday() != 0:  # Monday is 0
                last_complete_week = now - timedelta(days=now.weekday() + 1)
                data = data[data.index < last_complete_week]

        if isinstance(data.columns, pd.MultiIndex) and ticker in data.columns.levels[1]:
            data.columns = data.columns.get_level_values(0)
        elif not isinstance(data.columns, pd.MultiIndex) and 'Close' not in data.columns:
            st.error(f"'Close' price data not found for {ticker}.")
            return None
        elif isinstance(data.columns, pd.MultiIndex) and ticker not in data.columns.levels[1]:
            st.error(f"Ticker '{ticker}' not found in the multi-index columns.")
            return None

        if 'Close' in data.columns:
            if 'Adj Close' in data.columns:
                data = data[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']].astype(float)
            else:
                data = data[['Open', 'High', 'Low', 'Close', 'Volume']].astype(float)
        else:
            st.error(f"Could not find 'Close' data for {ticker}.")
            return None
        return data
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return None