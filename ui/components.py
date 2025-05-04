import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from utils.constants import nifty_50_tickers_yfinance

def sidebar_show_signals():
    selected_timeframes = st.sidebar.multiselect(
        "Select Timeframes for Analysis",
        ['1 Day', '1 Week', '1 Month'],
        default=['1 Week']
    )
    stock_tickers_show_signals = st.sidebar.multiselect(
        "Select Indian Stocks for Analysis",
        nifty_50_tickers_yfinance,
        # default=nifty_50_tickers_yfinance
        default=["RELIANCE.NS"]
    )
    return stock_tickers_show_signals, selected_timeframes

def sidebar_backtesting():
    default_ticker = "TCS.NS"
    try:
        default_index = nifty_50_tickers_yfinance.index(default_ticker)
    except ValueError:
        default_index = 0  # Fallback to the first ticker if default not found

    backtest_ticker = st.sidebar.selectbox(
        "Select Stock for Backtesting",
        nifty_50_tickers_yfinance,
        index=default_index
    )
    backtest_start_date = st.sidebar.date_input("Backtest Start Date")
    backtest_end_date = st.sidebar.date_input("Backtest End Date")
    backtest_strategy_option = st.sidebar.selectbox("Select Strategy for Backtesting", ["EMA Crossover", "SMA Price Crossover", "RSI Oversold Reversal", "MACD Crossover"])
    run_backtest = st.sidebar.button("Run Backtest")
    return backtest_ticker, backtest_start_date, backtest_end_date, backtest_strategy_option, run_backtest

def sidebar():
    app_mode = st.sidebar.radio(
        "Select Mode",
        ["Show Signals", "Backtesting"]
    )
    stock_tickers = []
    selected_analysis_timeframes = ['1 Day'] # Default
    backtest_ticker = None
    backtest_start_date = None
    backtest_end_date = None
    backtest_strategy_option = None
    run_backtest = False

    if app_mode == "Show Signals":
        stock_tickers, selected_analysis_timeframes = sidebar_show_signals()
    elif app_mode == "Backtesting":
        backtest_ticker, backtest_start_date, backtest_end_date, backtest_strategy_option, run_backtest = sidebar_backtesting()
        stock_tickers = [backtest_ticker] # For consistency in the return value

    return app_mode, stock_tickers, backtest_ticker, backtest_start_date, backtest_end_date, backtest_strategy_option, run_backtest, selected_analysis_timeframes
def display_latest_signals(data, breakout_signals, latest_entry_levels):
    st.subheader("Latest Breakout Signals and Potential Exit Levels:")
    latest_signals = breakout_signals.tail(1)
    if not latest_signals.empty and latest_signals.any(axis=1).iloc[0]:
        reasons = []
        signal_dates = latest_signals[latest_signals.any(axis=1)].index.tolist()
        entry_prices = {}

        if latest_signals['EMA Crossover'].iloc[0]:
            entry_price = latest_entry_levels.get('EMA Crossover')
            entry_prices['EMA Crossover'] = entry_price
            reasons.append(f"20-day EMA crossed above 50-day EMA (Entry: {'{:.2f}'.format(entry_price) if entry_price is not None else 'N/A'})")
        if latest_signals['SMA Price Crossover'].iloc[0]:
            entry_price = latest_entry_levels.get('SMA Price Crossover')
            entry_prices['SMA Price Crossover'] = entry_price
            reasons.append(f"Price crossed above 50-day SMA (Entry: {'{:.2f}'.format(entry_price) if entry_price is not None else 'N/A'})")
        if latest_signals['RSI Oversold Reversal'].iloc[0]:
            entry_price = latest_entry_levels.get('RSI Oversold Reversal')
            entry_prices['RSI Oversold Reversal'] = entry_price
            reasons.append(f"14-day RSI reversed from oversold (<30) (Entry: {'{:.2f}'.format(entry_price) if entry_price is not None else 'N/A'})")
        if latest_signals['MACD Crossover'].iloc[0]:
            entry_price = latest_entry_levels.get('MACD Crossover')
            entry_prices['MACD Crossover'] = entry_price
            reasons.append(f"MACD line crossed above Signal line (Entry: {'{:.2f}'.format(entry_price) if entry_price is not None else 'N/A'})")

        st.success(f"Breakout signal(s) detected on {signal_dates[0].strftime('%Y-%m-%d')}: {', '.join(reasons)}")
        st.dataframe(latest_signals[latest_signals.any(axis=1)])

        st.subheader("Potential Exit Levels:")
        exit_levels_data = {}
        signal_detected = False

        if latest_signals['EMA Crossover'].iloc[0]:
            signal_detected = True
            entry = entry_prices.get('EMA Crossover')
            low = data.iloc[-1]['Low'] # Using the low of the signal day as potential stop-loss
            if entry is not None and low is not None:
                risk = entry - low
                exit1 = entry + 1.5 * risk
                exit2 = entry + 2.5 * risk
                exit_levels_data['EMA Crossover'] = {'Exit Level 1': f"{exit1:.2f}", 'Exit Level 2': f"{exit2:.2f}"}

        if latest_signals['SMA Price Crossover'].iloc[0]:
            signal_detected = True
            entry = entry_prices.get('SMA Price Crossover')
            low = data.iloc[-1]['Low']
            if entry is not None and low is not None:
                risk = entry - low
                exit1 = entry + 1.5 * risk
                exit2 = entry + 2.5 * risk
                exit_levels_data['SMA Price Crossover'] = {'Exit Level 1': f"{exit1:.2f}", 'Exit Level 2': f"{exit2:.2f}"}

        if latest_signals['RSI Oversold Reversal'].iloc[0]:
            signal_detected = True
            entry = entry_prices.get('RSI Oversold Reversal')
            low = data.iloc[-1]['Low']
            if entry is not None and low is not None:
                risk = entry - low
                exit1 = entry + 1.5 * risk
                exit2 = entry + 2.5 * risk
                exit_levels_data['RSI Oversold Reversal'] = {'Exit Level 1': f"{exit1:.2f}", 'Exit Level 2': f"{exit2:.2f}"}

        if latest_signals['MACD Crossover'].iloc[0]:
            signal_detected = True
            entry = entry_prices.get('MACD Crossover')
            low = data.iloc[-1]['Low']
            if entry is not None and low is not None:
                risk = entry - low
                exit1 = entry + 1.5 * risk
                exit2 = entry + 2.5 * risk
                exit_levels_data['MACD Crossover'] = {'Exit Level 1': f"{exit1:.2f}", 'Exit Level 2': f"{exit2:.2f}"}

        if signal_detected and exit_levels_data:
            st.dataframe(pd.DataFrame.from_dict(exit_levels_data, orient='index'))
        elif not latest_signals.empty and latest_signals.any(axis=1).iloc[0]:
            st.info("Potential exit levels could not be calculated.")

    else:
        st.info("No breakout signals based on the selected strategies.")



def display_stock_chart(data, breakout_signals, latest_entry_levels=None):
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        row_heights=[3, 1, 1], vertical_spacing=0.03,
                        subplot_titles=('Price and Indicators', 'RSI (14)', 'MACD'))
    fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'],
                                 low=data['Low'], close=data['Close'], name='Candlestick'), row=1, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=data['EMA_20'], line=dict(color='blue'), name='EMA 20'), row=1, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=data['EMA_50'], line=dict(color='orange'), name='EMA 50'), row=1, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA_50'], line=dict(color='purple'), name='SMA 50'), row=1, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=data['EMA_200'], line=dict(color='pink'), name='EMA 200'), row=1, col=1)

    signal_points = data[breakout_signals.any(axis=1)]
    fig.add_trace(go.Scatter(x=signal_points.index, y=signal_points['High'],
                             mode='markers', marker=dict(symbol='triangle-up', size=10, color='green'),
                             name='Breakout Signal'), row=1, col=1)

    # RSI subplot
    fig.add_trace(go.Scatter(x=data.index, y=data['RSI_14'], line=dict(color='red'), name='RSI 14'), row=2, col=1)
    fig.add_hline(y=70, line=dict(color='grey', dash='dash'), row=2, col=1)
    fig.add_hline(y=30, line=dict(color='grey', dash='dash'), row=2, col=1)

    # MACD subplot
    fig.add_trace(go.Scatter(x=data.index, y=data['MACD'], line=dict(color='blue'), name='MACD'), row=3, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=data['Signal'], line=dict(color='orange'), name='Signal'), row=3, col=1)
    fig.add_trace(go.Bar(x=data.index, y=data['Histogram'], name='Histogram', marker_color=data['Histogram'].apply(lambda x: 'green' if x > 0 else 'red')), row=3, col=1)

    # Plotting exit levels if signals are present and levels are calculated
    if latest_entry_levels:
        if breakout_signals['EMA Crossover'].iloc[-1]:
            entry = latest_entry_levels.get('EMA Crossover')
            low = data.iloc[-1]['Low']
            if entry is not None and low is not None:
                risk = entry - low
                exit1 = entry + 1.5 * risk
                exit2 = entry + 2.5 * risk
                fig.add_hline(y=exit1, line=dict(color='green', dash='dash'), name='EMA Exit 1', row=1, col=1)
                fig.add_hline(y=exit2, line=dict(color='green', dash='dot'), name='EMA Exit 2', row=1, col=1)

        if breakout_signals['SMA Price Crossover'].iloc[-1]:
            entry = latest_entry_levels.get('SMA Price Crossover')
            low = data.iloc[-1]['Low']
            if entry is not None and low is not None:
                risk = entry - low
                exit1 = entry + 1.5 * risk
                exit2 = entry + 2.5 * risk
                fig.add_hline(y=exit1, line=dict(color='green', dash='dash'), name='SMA Exit 1', row=1, col=1)
                fig.add_hline(y=exit2, line=dict(color='green', dash='dot'), name='SMA Exit 2', row=1, col=1)

        if breakout_signals['RSI Oversold Reversal'].iloc[-1]:
            entry = latest_entry_levels.get('RSI Oversold Reversal')
            low = data.iloc[-1]['Low']
            if entry is not None and low is not None:
                risk = entry - low
                exit1 = entry + 1.5 * risk
                exit2 = entry + 2.5 * risk
                fig.add_hline(y=exit1, line=dict(color='green', dash='dash'), name='RSI Exit 1', row=1, col=1)
                fig.add_hline(y=exit2, line=dict(color='green', dash='dot'), name='RSI Exit 2', row=1, col=1)

        if breakout_signals['MACD Crossover'].iloc[-1]:
            entry = latest_entry_levels.get('MACD Crossover')
            low = data.iloc[-1]['Low']
            if entry is not None and low is not None:
                risk = entry - low
                exit1 = entry + 1.5 * risk
                exit2 = entry + 2.5 * risk
                fig.add_hline(y=exit1, line=dict(color='green', dash='dash'), name='MACD Exit 1', row=1, col=1)
                fig.add_hline(y=exit2, line=dict(color='green', dash='dot'), name='MACD Exit 2', row=1, col=1)

    fig.update_layout(xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

def display_indicator_values(data, ticker):
    if st.checkbox(f"Show Indicator Values for {ticker}"):
        st.subheader("Indicator Values:")
        st.dataframe(data.tail())