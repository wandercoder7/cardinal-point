import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from utils.date_utils import get_current_time
import logging
from utils.date_utils import get_start_date, is_market_time, get_end_date

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

@st.cache_data
def fetch_stock_data(ticker, period="1y", interval="1d", as_of_date=None):
    """
    Fetches historical stock data from Yahoo Finance.

    Args:
        ticker (str): Stock ticker symbol.
        period (str): Period for fetching data (e.g., '10y', '5y', '2y', '1y', '6mo').
        interval (str): Data interval (e.g., '1d', '1wk').

    Returns:
        pd.DataFrame: DataFrame containing the stock data.
    """
    auto_adjust_data = False
    try:
        data = None
        if(as_of_date is not None):
            start = get_start_date(period, as_of_date)
            end = get_end_date(as_of_date, interval)
            log.info(f"fetching data for {ticker} from {start} to {as_of_date} with interval {interval}")
            data = yf.download(ticker, start=start, end=end, interval=interval, auto_adjust=auto_adjust_data, multi_level_index=False)
        else:
            log.info(f"fetching data for {ticker} with period {period} and interval {interval}")
            data = yf.download(ticker, period=period, interval=interval, auto_adjust=auto_adjust_data, multi_level_index=False)

        if data.empty:
            st.warning(f"No data found for {ticker}.")
            return None
       
        # data = cleanup_data(interval, data)

        if 'Close' in data.columns:
            data = cleanup_columns(data)
        else:
            st.error(f"Could not find 'Close' data for {ticker}.")
            return None
        return data
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        log.error(f"Could not find 'Close' data for {ticker}: {e}")

        return None
    
def cleanup_data(interval, data):
    # Remove incomplete intervals
    now = get_current_time()
    if interval == "1d":
        # Remove today's data if the current time is before 4 PM
        if is_market_time(now) and data.index[-1].date() == now.date():
            data = data.iloc[:-1]
    elif interval == "1wk":
        # Remove the current week's data if today is not Monday
        if now.weekday() != 0:  # Monday is 0
            last_complete_week = now - timedelta(days=now.weekday() + 1)
            data = data[data.index < last_complete_week]
    return data

def cleanup_columns(data):
    if 'Adj Close' in data.columns:
        data = data[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']].astype(float)
    else:
        data = data[['Open', 'High', 'Low', 'Close', 'Volume']].astype(float)
    return data
