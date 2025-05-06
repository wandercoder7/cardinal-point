import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from utils.date_utils import getCurrentTime
from logging import getLogger
log = getLogger(__name__)

@st.cache_data
def fetch_stock_data(ticker, period="1y", interval="1d", as_of_date=None):
    """
    Fetches historical stock data from Yahoo Finance.

    Args:
        ticker (str): Stock ticker symbol.
        period (str): Period for fetching data (e.g., '10y', '5y', '1y', '6mo').
        interval (str): Data interval (e.g., '1d', '1wk').

    Returns:
        pd.DataFrame: DataFrame containing the stock data.
    """
    auto_adjust_data = False
    try:
        data = None
        if(as_of_date is not None):
            start = get_start_date(period, as_of_date)
            data = yf.download(ticker, start=start, end=as_of_date, interval=interval, auto_adjust=auto_adjust_data, multi_level_index=False)
        else:
            data = yf.download(ticker, period=period, interval=interval, auto_adjust=auto_adjust_data, multi_level_index=False)

        if data.empty:
            st.warning(f"No data found for {ticker}.")
            return None
        # Remove incomplete intervals
        now = getCurrentTime()
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
        log.error(f"Could not find 'Close' data for {ticker}: {e}")

        return None

def get_start_date(period, as_of_date):
    start = as_of_date
    # Adjust the start based on the as_of_date and period
    if(period == "1y"):
        start = start - timedelta(days=365)
    elif(period == "6mo"):
        start = start - timedelta(days=183)
    elif(period == "5y"):
        start = start - timedelta(days=1825)
    elif(period == "10y"):  
        start = start - timedelta(days=3650)
    return start