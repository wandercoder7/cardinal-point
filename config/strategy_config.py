from strategies.swing_strategies import (
    ema_crossover_long,
    sma_price_crossover_long,
    rsi_oversold_reversal_long,
    macd_crossover_long,
    ema_200_weekly_breakout
)
from strategies.fibonacci_strategies import fibonacci_retracement_strategy

# Define common strategy objects
EMA_CROSSOVER = {
    'name': 'EMA Crossover',
    'function': ema_crossover_long,
}

SMA_PRICE_CROSSOVER = {
    'name': 'SMA Price Crossover',
    'function': sma_price_crossover_long,
}

RSI_OVERSOLD_REVERSAL = {
    'name': 'RSI Oversold Reversal',
    'function': rsi_oversold_reversal_long,
}

MACD_CROSSOVER = {
    'name': 'MACD Crossover',
    'function': macd_crossover_long,
}

EMA_200_BREAKOUT = {
    'name': 'EMA 200 Breakout',
    'function': ema_200_weekly_breakout,
}

FIBONACCI_RETRACEMENT = {
    'name': 'Fibonacci Retracement',
    'function': fibonacci_retracement_strategy,
}

# Strategy configuration by timeframe
daily_strategies = [
    EMA_CROSSOVER,
    SMA_PRICE_CROSSOVER,
    RSI_OVERSOLD_REVERSAL,
    MACD_CROSSOVER,
    EMA_200_BREAKOUT,
]

weekly_strategies = [
    RSI_OVERSOLD_REVERSAL,
    MACD_CROSSOVER,
    EMA_200_BREAKOUT,
    # FIBONACCI_RETRACEMENT
]

STRATEGY_CONFIG = {
    '1 Day': daily_strategies,
    '1 Week': weekly_strategies,
    # '1 Month': [] # Commented out as no strategies configured for monthly timeframe
}
