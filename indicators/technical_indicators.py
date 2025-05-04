import pandas as pd
import ta

def calculate_ema(data: pd.DataFrame, period: int, column: str = 'Close') -> pd.Series:
    """
    Calculates the Exponential Moving Average (EMA).

    Args:
        data (pd.DataFrame): DataFrame containing the stock data.
        period (int): The time period for the EMA calculation.
        column (str): The column to calculate the EMA on (default: 'Close').

    Returns:
        pd.Series: A Series containing the EMA values.
    """
    return data[column].ewm(span=period, adjust=False).mean()

def calculate_sma(data: pd.DataFrame, period: int, column: str = 'Close') -> pd.Series:
    """
    Calculates the Simple Moving Average (SMA).

    Args:
        data (pd.DataFrame): DataFrame containing the stock data.
        period (int): The time period for the SMA calculation.
        column (str): The column to calculate the SMA on (default: 'Close').

    Returns:
        pd.Series: A Series containing the SMA values.
    """
    return data[column].rolling(window=period).mean()

def calculate_rsi(data: pd.DataFrame, period: int = 14, column: str = 'Close') -> pd.Series:
    """
    Calculates the Relative Strength Index (RSI).

    Args:
        data (pd.DataFrame): DataFrame containing the stock data.
        period (int): The time period for the RSI calculation (default: 14).
        column (str): The column to calculate the RSI on (default: 'Close').

    Returns:
        pd.Series: A Series containing the RSI values.
    """
    delta = data[column].diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

import pandas as pd
import ta

# (Your existing calculate_ema, calculate_sma, calculate_rsi functions)

def calculate_macd(data: pd.DataFrame, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9, column: str = 'Close') -> pd.DataFrame:
    """
    Calculates the Moving Average Convergence Divergence (MACD).

    Args:
        data (pd.DataFrame): DataFrame containing the stock data.
        fast_period (int): The period for the fast EMA (default: 12).
        slow_period (int): The period for the slow EMA (default: 26).
        signal_period (int): The period for the signal EMA (default: 9).
        column (str): The column to calculate the MACD on (default: 'Close').

    Returns:
        pd.DataFrame: DataFrame with 'MACD', 'Signal', and 'Histogram' columns.
    """
    macd_indicator = ta.trend.MACD(data[column], window_fast=fast_period, window_slow=slow_period, window_sign=signal_period)
    macd = macd_indicator.macd()
    signal = macd_indicator.macd_signal()
    histogram = macd_indicator.macd_diff()
    return pd.DataFrame({'MACD': macd, 'Signal': signal, 'Histogram': histogram})

# We don't need a separate function for volume for now, we can just use the 'Volume' column directly.