from indicators.technical_indicators import calculate_ema, calculate_sma, calculate_rsi, calculate_macd
import pandas as pd

def calculate_indicators(data: pd.DataFrame):
    data['EMA_200'] = calculate_ema(data, 200, column='Close')
    data['EMA_20'] = calculate_ema(data, 20, column='Close')
    data['SMA_50'] = calculate_sma(data, 50, column='Close')
    data['RSI_14'] = calculate_rsi(data, column='Close')
    data['EMA_50'] = calculate_ema(data, 50, column='Close')
    macd_df = calculate_macd(data)
    data = pd.concat([data, macd_df], axis=1)
    return data