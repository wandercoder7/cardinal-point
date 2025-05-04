import streamlit as st
from backtesting.backtester import backtest_strategy
from utils.calculations import calculate_indicators
from strategies.swing_strategies import ema_crossover_long, sma_price_crossover_long, rsi_oversold_reversal_long, macd_crossover_long

def run_backtest(backtest_ticker, backtest_start_date, backtest_end_date, backtest_strategy_option):
    if backtest_ticker and backtest_start_date and backtest_end_date and backtest_start_date < backtest_end_date:
        from utils.data_fetching import fetch_stock_data # Import here to avoid circular dependency
        backtest_data = fetch_stock_data(backtest_ticker, period=f"{(backtest_end_date - backtest_start_date).days}d")
        if backtest_data is not None:
            backtest_data = backtest_data[backtest_start_date:backtest_end_date].copy()
            backtest_data = calculate_indicators(backtest_data)

            selected_strategy_func = None
            if backtest_strategy_option == "EMA Crossover":
                selected_strategy_func = ema_crossover_long
            elif backtest_strategy_option == "SMA Price Crossover":
                selected_strategy_func = sma_price_crossover_long
            elif backtest_strategy_option == "RSI Oversold Reversal":
                selected_strategy_func = rsi_oversold_reversal_long
            elif backtest_strategy_option == "MACD Crossover":
                selected_strategy_func = macd_crossover_long

            if selected_strategy_func:
                positions, trades_df = backtest_strategy(backtest_data, selected_strategy_func)
                display_backtesting_results(trades_df, backtest_ticker, backtest_strategy_option, backtest_start_date, backtest_end_date)
            else:
                st.error("Strategy function not found.")
        else:
            st.error("Could not retrieve data for backtesting.")
    else:
        st.warning("Please select a stock, start date, end date, and strategy for backtesting.")
    st.markdown("---")

def display_backtesting_results(trades_df, ticker, strategy_name, start_date, end_date):
    st.subheader(f"Backtesting Results for {ticker} using {strategy_name} ({start_date} to {end_date})")
    if not trades_df.empty:
        num_trades = len(trades_df)
        winning_trades = len(trades_df[trades_df['profit_loss_percentage'] > 0])
        win_rate = (winning_trades / num_trades) * 100 if num_trades > 0 else 0
        average_profit_loss = trades_df['profit_loss_percentage'].mean() * 100
        st.metric("Total Trades", num_trades)
        st.metric("Win Rate (%)", f"{win_rate:.2f}")
        st.metric("Average Profit/Loss per Trade (%)", f"{average_profit_loss:.2f}")
        st.subheader("Individual Trades:")
        st.dataframe(trades_df)
    else:
        st.info("No trades were executed during the backtesting period.")