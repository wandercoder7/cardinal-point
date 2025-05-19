import pandas as pd
import numpy as np

def identify_swing_points(data, window=10):
    """Identify swing highs and lows in the data"""
    highs = data['High']
    lows = data['Low']
    
    # Initialize swing points
    swing_highs = pd.Series(index=data.index, dtype=float)
    swing_lows = pd.Series(index=data.index, dtype=float)
    
    for i in range(window, len(data) - window):
        # Check for swing high
        if all(highs[i] > highs[i-window:i]) and all(highs[i] > highs[i+1:i+window+1]):
            swing_highs[i] = highs[i]
        # Check for swing low
        if all(lows[i] < lows[i-window:i]) and all(lows[i] < lows[i+1:i+window+1]):
            swing_lows[i] = lows[i]
    
    return swing_highs, swing_lows

def fibonacci_retracement_strategy(data: pd.DataFrame, window: int = 10, trend_periods: int = 12) -> pd.DataFrame:
    """
    Identifies potential buy signals based on Fibonacci retracement levels.
    Specifically looks for touches of the 50% retracement level after an uptrend.
    """
    swing_highs, swing_lows = identify_swing_points(data, window)
    
    # Initialize signal series
    signal = pd.Series(False, index=data.index)
    entry_level = pd.Series(index=data.index, dtype=float)
    
    # Look for the most recent valid swing high and low
    for i in range(len(data) - 1, window, -1):
        if i < trend_periods:
            continue
            
        # Find the most recent swing high before current point
        recent_high = swing_highs.iloc[i-trend_periods:i].max()
        if pd.isna(recent_high):
            continue
            
        # Find the subsequent low using iloc for integer-based indexing
        high_idx = swing_highs.iloc[i-trend_periods:i].idxmax()
        current_idx = data.index[i]
        mask = (data.index >= high_idx) & (data.index <= current_idx)
        subsequent_low = data.loc[mask, 'Low'].min()
        
        if pd.isna(subsequent_low) or recent_high <= subsequent_low:
            continue
        
        # Calculate Fibonacci levels
        diff = recent_high - subsequent_low
        fib_50 = subsequent_low + (diff * 0.5)
        
        # Check if current candle touches 50% level
        current_candle = data.iloc[i]
        touches_fib_50 = (current_candle['Low'] <= fib_50 <= current_candle['High'])
        
        # Additional confirmation: prior uptrend
        prior_uptrend = data.iloc[i-trend_periods:i]['Close'].is_monotonic_increasing
        
        if touches_fib_50 and prior_uptrend:
            signal.iloc[i] = True
            entry_level.iloc[i] = current_candle['Close']
    
    return pd.DataFrame({
        'signal': signal,
        'entry_level': entry_level
    })
