import pandas as pd
from scipy.signal import argrelextrema
import numpy as np

def identify_support_resistance(data: pd.DataFrame, lookahead=20):
    """
    Identifies potential support and resistance levels based on local minima and maxima.
    """
    lows = data['Low'].values
    highs = data['High'].values
    min_indices = argrelextrema(lows, np.less_equal, order=lookahead)[0]
    max_indices = argrelextrema(highs, np.greater_equal, order=lookahead)[0]

    support_levels = data['Low'].iloc[min_indices].unique()
    resistance_levels = data['High'].iloc[max_indices].unique()

    return support_levels, resistance_levels

def backtest_strategy(data: pd.DataFrame, strategy: callable, lookahead_sr=20, stop_loss_percentage=0.02):
    """
    Backtests a given trading strategy on historical data with support/resistance based exits.

    Args:
        data (pd.DataFrame): DataFrame containing historical stock data with necessary indicators.
        strategy (callable): A function that takes the data and returns a Series of boolean signals (True for buy).
        lookahead_sr (int): Lookahead window for identifying support and resistance.
        stop_loss_percentage (float): Percentage for setting the stop-loss below entry.

    Returns:
        pandas.DataFrame: DataFrame with trading signals and portfolio status.
    """
    signals_df = strategy(data)

    # Ensure signals_df has a 'signal' column
    if 'signal' not in signals_df.columns:
        raise ValueError("The strategy function must return a DataFrame with a 'signal' column.")

    signals = signals_df['signal']
    positions = pd.Series(0, index=data.index)  # Initialize with 0 for all dates
    in_position = False
    entry_price = 0
    trades = []

    for i in data.index:
        support_levels, resistance_levels = identify_support_resistance(data.iloc[:data.index.get_loc(i) + 1], lookahead=lookahead_sr)
        current_price = data['Close'][i]
        if i in signals.index:
            if signals[i] and not in_position:
                positions[i] = 1  # Enter long position
                in_position = True
                entry_price = data['Close'][i]
                stop_loss_level = entry_price * (1 - stop_loss_percentage)
            elif in_position:
                # Exit if price reaches a past resistance level (within a tolerance)
                relevant_resistance = resistance_levels[resistance_levels > entry_price]
                if not signals[i] and i in data.index:
                    positions[i] = 0 # Exit long position
                    in_position = False
                    exit_price = current_price
                    profit_loss_percentage = (exit_price - entry_price) / entry_price
                    absolute_profit_loss = exit_price - entry_price
                    trades.append({'entry_date': positions[positions == 1].index[-1], 'entry_price': entry_price, 'exit_date': i, 'exit_price': exit_price, 'profit_loss_percentage': profit_loss_percentage, 'absolute_profit_loss': absolute_profit_loss, 'exit_reason': 'Resistance'})
                    entry_price = 0
                    stop_loss_level = 0
        # If the date from data.index is not in signals.index, maintain the previous position
        elif in_position:
            positions[i] = 1
        else:
            positions[i] = 0

    trades_df = pd.DataFrame(trades)
    return positions, trades_df