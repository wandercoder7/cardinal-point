import streamlit as st
import pandas as pd
from utils.data_fetching import fetch_stock_data
from utils.calculations import calculate_indicators
from ui.components import display_indicator_values, display_stock_chart
from ui.signal_display import display_signals_table
from config.strategy_config import STRATEGY_CONFIG
from utils.constants import TIMEFRAMES

def calculate_signals_for_ticker(data, timeframe):
    """Calculate signals based on configured strategies for the timeframe"""
    if timeframe not in STRATEGY_CONFIG:
        return pd.DataFrame(), {}
    
    all_signals = pd.DataFrame(index=data.index)
    entry_levels = {}
    
    for strategy in STRATEGY_CONFIG[timeframe]:
        strategy_func = strategy['function']
        strategy_name = strategy['name']
        signal_df = strategy_func(data)
        all_signals[strategy_name] = signal_df['signal']
        if signal_df['signal'].iloc[-1]:
            entry_levels[strategy_name] = signal_df['entry_level'].iloc[-1]
    
    return all_signals, entry_levels

def show_signals(stock_tickers, selected_timeframes, as_of_date):
    fetched_data = {}
    tickers_with_signals_data = []

    for ticker in stock_tickers:
        signals_for_ticker, latest_close_1d, all_data_fetched = process_ticker_signals(
            ticker, selected_timeframes, fetched_data, as_of_date
        )
        if all_data_fetched and any(
            signals_for_ticker.get(f'{tf} Signals') != "No Signal" for tf in selected_timeframes
        ):
            if latest_close_1d:
                signals_for_ticker['Last Close'] = latest_close_1d
            tickers_with_signals_data.append(signals_for_ticker)

    display_signals_summary(tickers_with_signals_data, selected_timeframes, fetched_data)

def process_ticker_signals(ticker, selected_timeframes, fetched_data, as_of_date):
    signals_for_ticker = {'Ticker': ticker}
    all_data_fetched = True
    latest_close_1d = None

    for timeframe_name in selected_timeframes:
        if timeframe_name not in STRATEGY_CONFIG:
            continue

        timeframe_value, fetch_period = TIMEFRAMES.get(timeframe_name, ('1d', '6mo'))
        if not timeframe_value:
            continue

        stock_data = fetch_or_get_stock_data(ticker, timeframe_value, fetch_period, fetched_data, as_of_date)
        if stock_data is None:
            all_data_fetched = False
            break

        data = calculate_indicators(stock_data.copy())
        breakout_signals, entry_levels = calculate_signals_for_ticker(data, timeframe_name)
        latest_signal = breakout_signals.tail(1)

        latest_close_1d = update_latest_close(data, timeframe_name, latest_close_1d)
        update_signals_for_ticker(signals_for_ticker, timeframe_name, latest_signal)

    return signals_for_ticker, latest_close_1d, all_data_fetched

def fetch_or_get_stock_data(ticker, timeframe_value, fetch_period, fetched_data, as_of_date):
    if ticker not in fetched_data or timeframe_value not in fetched_data[ticker]:
        stock_data = fetch_stock_data(ticker, period=fetch_period, interval=timeframe_value, as_of_date=as_of_date)
        if stock_data is not None:
            if ticker not in fetched_data:
                fetched_data[ticker] = {}
            fetched_data[ticker][timeframe_value] = stock_data.copy()
        return stock_data
    return fetched_data[ticker][timeframe_value]

def update_latest_close(data, timeframe_name, latest_close_1d):
    if timeframe_name == '1 Day' and not data.empty:
        return f"{data['Close'].iloc[-1]:.2f}"
    elif timeframe_name == '1 Day':
        return "N/A"
    return latest_close_1d

def update_signals_for_ticker(signals_for_ticker, timeframe_name, latest_signal):
    detected_signals = []
    if not latest_signal.empty and latest_signal.any(axis=1).iloc[0]:
        for strategy_name in latest_signal.columns:
            if latest_signal[strategy_name].iloc[0]:
                detected_signals.append(strategy_name)

    signals_for_ticker[f'{timeframe_name} Signals'] = ', '.join(detected_signals) if detected_signals else "No Signal"
    if not latest_signal.empty:
        signal_dates = latest_signal[latest_signal.any(axis=1)].index.strftime('%Y-%m-%d')
        signals_for_ticker[f'{timeframe_name} Signal Date'] = signal_dates[-1] if not signal_dates.empty else "N/A"
    else:
        signals_for_ticker[f'{timeframe_name} Signal Date'] = "N/A"

def display_signals_summary(tickers_with_signals_data, selected_timeframes, fetched_data):
    if not tickers_with_signals_data:
        st.info(f"No breakout signals found for the selected tickers across the timeframes: {', '.join(selected_timeframes)}.")
    else:
        signals_df = pd.DataFrame(tickers_with_signals_data)
        selected_ticker_timeframe = display_signals_table(signals_df, selected_timeframes)

        if selected_ticker_timeframe and selected_ticker_timeframe[0]:
            display_selected_ticker_chart(selected_ticker_timeframe, fetched_data)

def display_selected_ticker_chart(selected_ticker_timeframe, fetched_data):
    selected_ticker = selected_ticker_timeframe[0]
    selected_tf_name = selected_ticker_timeframe[1]
    timeframe_value, _ = TIMEFRAMES[selected_tf_name]

    st.subheader(f"Chart for {selected_ticker} ({selected_tf_name})")
    if selected_ticker in fetched_data and timeframe_value in fetched_data[selected_ticker]:
        data_selected = fetched_data[selected_ticker][timeframe_value].copy()
        data_selected = calculate_indicators(data_selected)
        breakout_signals_selected, latest_entry_levels_selected = calculate_signals_for_ticker(data_selected, selected_tf_name)
        display_stock_chart(data_selected, breakout_signals_selected, latest_entry_levels_selected)
        display_indicator_values(data_selected, selected_ticker)
    else:
        st.error(f"Could not retrieve data for {selected_ticker} at {selected_tf_name}.")
    st.markdown("---")