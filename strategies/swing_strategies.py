import pandas as pd

def ema_crossover_long(data: pd.DataFrame, short_period: int = 20, long_period: int = 50, volume_multiplier: float = 1.5) -> pd.DataFrame:
    short_ema_col = f'EMA_{short_period}'
    long_ema_col = f'EMA_{long_period}'
    if short_ema_col not in data.columns or long_ema_col not in data.columns or 'Volume' not in data.columns:
        raise ValueError(...)
    average_volume = data['Volume'].rolling(window=20).mean()
    crossover = (data[short_ema_col] > data[long_ema_col]) & (data[short_ema_col].shift(1) <= data[long_ema_col].shift(1))
    volume_spike = data['Volume'] > (volume_multiplier * average_volume)
    signal = crossover & volume_spike
    entry_level = data['High'][signal]
    return pd.DataFrame({'signal': signal, 'entry_level': entry_level})

def sma_price_crossover_long(data: pd.DataFrame, sma_period: int = 50) -> pd.DataFrame:
    sma_col = f'SMA_{sma_period}'
    if sma_col not in data.columns or 'Close' not in data.columns:
        raise ValueError(...)
    crossover = (data['Close'] > data[sma_col]) & (data['Close'].shift(1) <= data[sma_col].shift(1))
    signal = crossover
    entry_level = data['High'][signal]
    return pd.DataFrame({'signal': signal, 'entry_level': entry_level})

def rsi_oversold_reversal_long(data: pd.DataFrame, rsi_period: int = 14, oversold_level: int = 30) -> pd.DataFrame:
    rsi_col = f'RSI_{rsi_period}'
    if rsi_col not in data.columns:
        raise ValueError(...)
    reversal = (data[rsi_col] > oversold_level) & (data[rsi_col].shift(1) <= oversold_level)
    signal = reversal
    entry_level = data['High'][signal]
    return pd.DataFrame({'signal': signal, 'entry_level': entry_level})

def macd_crossover_long(data: pd.DataFrame) -> pd.DataFrame:
    if 'MACD' not in data.columns or 'Signal' not in data.columns:
        raise ValueError(...)
    crossover = (data['MACD'] > data['Signal']) & (data['MACD'].shift(1) <= data['Signal'].shift(1))
    signal = crossover
    entry_level = data['High'][signal]
    return pd.DataFrame({'signal': signal, 'entry_level': entry_level})

def ema_200_weekly_breakout(data: pd.DataFrame):
    """
    Generates a buy signal if the last weekly close is above the 200-week EMA.
    """
    open = data['Open'].iloc[-1]
    close = data['Close'].iloc[-1]
    low = data['Low'].iloc[-1]
    ema_200 = data['EMA_200'].iloc[-1]
    signal = (close > ema_200) and (open <= ema_200 or low <= ema_200) and (close > open)
    # To align with the existing flow, create a 'signal' column with the last value applied to the last row
    data['signal'] = False
    if signal:
        data.loc[data.index[-1], 'signal'] = True
    data['entry_level'] = data['Close'].where(data['signal'])
    return data[['signal', 'entry_level', 'EMA_200']]