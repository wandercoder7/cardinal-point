from strategies.swing_strategies import (
    ema_crossover_long,
    sma_price_crossover_long,
    rsi_oversold_reversal_long,
    macd_crossover_long,
    ema_200_weekly_breakout
)

# Strategy configuration by timeframe
STRATEGY_CONFIG = {
    '1 Day': [
        {
            'name': 'EMA Crossover',
            'function': ema_crossover_long,
        },
        {
            'name': 'SMA Price Crossover',
            'function': sma_price_crossover_long,
        },
        {
            'name': 'RSI Oversold Reversal',
            'function': rsi_oversold_reversal_long,
        },
        {
            'name': 'MACD Crossover',
            'function': macd_crossover_long,
        }
    ],
    '1 Week': [
        {
            'name': 'EMA 200 Breakout',
            'function': ema_200_weekly_breakout,
        }
    ],
    # '1 Month': [] # Commented out as no strategies configured for monthly timeframe
}
