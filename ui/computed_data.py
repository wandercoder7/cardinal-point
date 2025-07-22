import streamlit as st
import pandas as pd
from utils.data_fetching import fetch_stock_data
from utils.calculations import calculate_indicators
from utils.constants import TIMEFRAMES
from config.strategy_config import STRATEGY_CONFIG
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def show_computed_data(ticker, timeframe, as_of_date):
    """Display computed technical indicators and data for a given ticker and timeframe"""
    
    timeframe_value, fetch_period = TIMEFRAMES.get(timeframe, ('1d', '6mo'))
    if not timeframe_value:
        st.error(f"Invalid timeframe: {timeframe}")
        return

    # Fetch data
    stock_data = fetch_stock_data(ticker, period=fetch_period, interval=timeframe_value, as_of_date=as_of_date)
    if stock_data is None:
        st.error(f"Could not fetch data for {ticker}")
        return

    # Calculate indicators
    data = calculate_indicators(stock_data.copy())
    # Create a DataFrame with all relevant indicators
    display_data = pd.DataFrame()
    display_data['Date'] = data.index
    display_data['Open'] = data['Open']
    display_data['High'] = data['High']
    display_data['Low'] = data['Low']
    display_data['Close'] = data['Close']
    display_data['Volume'] = data['Volume']
    display_data['EMA_20'] = data['EMA_20']
    display_data['EMA_50'] = data['EMA_50']
    display_data['EMA_200'] = data['EMA_200']
    display_data['SMA_50'] = data['SMA_50']
    display_data['RSI_14'] = data['RSI_14']
    display_data['MACD'] = data['MACD']
    display_data['Signal'] = data['Signal']
    display_data['Histogram'] = data['Histogram']

    # Display the data
    st.subheader(f"Computed Data for {ticker} ({timeframe})")
    st.dataframe(data.style.format({
        'Open': '{:.2f}',
        'High': '{:.2f}',
        'Low': '{:.2f}',
        'Close': '{:.2f}',
        'Volume': '{:,.0f}',
        'EMA_20': '{:.2f}',
        'EMA_50': '{:.2f}',
        'EMA_200': '{:.2f}',
        'SMA_50': '{:.2f}',
        'RSI_14': '{:.2f}',
        'MACD': '{:.4f}',
        'Signal': '{:.4f}',
        'Histogram': '{:.4f}'
    }))