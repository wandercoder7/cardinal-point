import pandas as pd

def backtest_strategy(data: pd.DataFrame, strategy: callable):
    """
    Backtests a given trading strategy on historical data.

    Args:
        data (pd.DataFrame): DataFrame containing historical stock data with necessary indicators.
        strategy (callable): A function that takes the data and returns a DataFrame with 'signal' and optionally 'entry_level' columns, indexed by date.

    Returns:
        pandas.DataFrame: DataFrame with trading signals and portfolio status.
    """
    print("Backtest Data Index:")
    print(data.index[:5])
    signals_df = strategy(data)
    print("\nSignals DataFrame Index:")
    print(signals_df.index[:5])

    # Ensure signals_df has a 'signal' column
    if 'signal' not in signals_df.columns:
        raise ValueError("The strategy function must return a DataFrame with a 'signal' column.")

    signals = signals_df['signal']
    positions = pd.Series(0, index=data.index)  # Initialize with 0 for all dates
    in_position = False
    entry_price = 0
    trades = []

    for i in data.index:
        if i in signals.index:
            if signals[i] and not in_position:
                positions[i] = 1  # Enter long position
                in_position = True
                entry_price = data['Close'][i]
            elif in_position:
                if not signals[i] and i in data.index:
                    positions[i] = 0 # Exit long position
                    in_position = False
                    exit_price = data['Close'][i]
                    profit_loss = (exit_price - entry_price) / entry_price
                    trades.append({'entry_date': i, 'entry_price': entry_price, 'exit_date': i, 'exit_price': exit_price, 'profit_loss': profit_loss})
        # If the date from data.index is not in signals.index, maintain the previous position
        elif in_position:
            positions[i] = 1
        else:
            positions[i] = 0

    trades_df = pd.DataFrame(trades)
    return positions, trades_df