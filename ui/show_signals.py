import streamlit as st
import pandas as pd
from utils.data_fetching import fetch_stock_data
from utils.calculations import calculate_indicators
from strategies.swing_strategies import ema_crossover_long, sma_price_crossover_long, rsi_oversold_reversal_long, macd_crossover_long,ema_200_weekly_breakout
from ui.components import display_indicator_values, display_stock_chart
from ui.signal_display import display_signals_table

TIMEFRAMES = {'1 Day': ('1d', '1y'), '1 Week': ('1wk', '10y'), '1 Month': ('1mo', '10y')}

def calculate_signals_for_ticker(data):
    ema_signal_df = ema_crossover_long(data)
    sma_signal_df = sma_price_crossover_long(data)
    rsi_signal_df = rsi_oversold_reversal_long(data)
    macd_signal_df = macd_crossover_long(data)
    ema_200_signal_df = ema_200_weekly_breakout(data)
    breakout_signals = pd.DataFrame({
        'EMA Crossover': ema_signal_df['signal'],
        'SMA Price Crossover': sma_signal_df['signal'],
        'RSI Oversold Reversal': rsi_signal_df['signal'],
        'MACD Crossover': macd_signal_df['signal'],
        'EMA 200': ema_200_signal_df['signal'],
    }, index=data.index)
    return breakout_signals, {
        'EMA Crossover': ema_signal_df['entry_level'].iloc[-1] if not ema_signal_df.empty and ema_signal_df['signal'].iloc[-1] else None,
        'SMA Price Crossover': sma_signal_df['entry_level'].iloc[-1] if not sma_signal_df.empty and sma_signal_df['signal'].iloc[-1] else None,
        'RSI Oversold Reversal': rsi_signal_df['entry_level'].iloc[-1] if not rsi_signal_df.empty and rsi_signal_df['signal'].iloc[-1] else None,
        'MACD Crossover': macd_signal_df['entry_level'].iloc[-1] if not macd_signal_df.empty and macd_signal_df['signal'].iloc[-1] else None,
        'EMA 200': ema_200_signal_df['entry_level'].iloc[-1] if not ema_200_signal_df.empty and ema_200_signal_df['signal'].iloc[-1] else None,
    }

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
        timeframe_value, fetch_period = TIMEFRAMES.get(timeframe_name, ('1d', '6mo'))
        if not timeframe_value:
            continue

        stock_data = fetch_or_get_stock_data(ticker, timeframe_value, fetch_period, fetched_data, as_of_date)
        if stock_data is None:
            all_data_fetched = False
            break

        data = calculate_indicators(stock_data.copy())
        breakout_signals, _ = calculate_signals_for_ticker(data)
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
        if latest_signal['EMA Crossover'].iloc[0]:
            detected_signals.append("EMA")
        if latest_signal['SMA Price Crossover'].iloc[0]:
            detected_signals.append("SMA")
        if latest_signal['RSI Oversold Reversal'].iloc[0]:
            detected_signals.append("RSI")
        if latest_signal['MACD Crossover'].iloc[0]:
            detected_signals.append("MACD")
        if latest_signal['EMA 200'].iloc[0]:
            detected_signals.append("EMA 200")

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
        breakout_signals_selected, latest_entry_levels_selected = calculate_signals_for_ticker(data_selected)
        display_stock_chart(data_selected, breakout_signals_selected, latest_entry_levels_selected)
        display_indicator_values(data_selected, selected_ticker)
    else:
        st.error(f"Could not retrieve data for {selected_ticker} at {selected_tf_name}.")
    st.markdown("---")