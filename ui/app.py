import streamlit as st
import sys
import os

# Get the absolute path to the project's root directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from ui.components import sidebar
from ui.show_signals import show_signals
from backtesting.ui import run_backtest
from utils.date_utils import getCurrentTime

if __name__ == '__main__':
    current_time = getCurrentTime()
    st.title(f"Check Trend ({current_time})")

    app_mode = st.sidebar.radio(
        "Select Mode",
        ["Show Signals", "Backtesting"]
    )

    if app_mode == "Backtesting":
        stock_tickers, backtest_ticker, backtest_start_date, backtest_end_date, backtest_strategy_option, run_backtest_button, selected_analysis_timeframes = sidebar(app_mode)
        run_backtest(backtest_ticker, backtest_start_date, backtest_end_date, backtest_strategy_option)
    elif app_mode == "Show Signals":
        stock_tickers, selected_analysis_timeframes, as_of_date = sidebar(app_mode)
        show_signals(stock_tickers, selected_analysis_timeframes, as_of_date)