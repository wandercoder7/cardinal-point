import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.data_fetching import fetch_stock_data
from utils.constants import TIMEFRAMES
from strategies.fibonacci_strategies import identify_swing_points

class FibonacciAnalysis:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        
    def calculate_fibonacci_levels(self, high: float, low: float) -> dict:
        price_range = high - low
        return {
            'High': high,
            'Low': low,
            '0.236': low + (price_range * 0.236),
            '0.382': low + (price_range * 0.382),
            '0.500': low + (price_range * 0.500),
            '0.618': low + (price_range * 0.618),
            '0.786': low + (price_range * 0.786),
        }
    
    def get_recent_swings(self, swing_points: pd.Series, num_swings: int = 5) -> tuple:
        recent_points = swing_points.dropna().iloc[-num_swings:]
        if not recent_points.empty:
            start_date = recent_points.index[0]
            mask = self.data.index >= start_date
            return recent_points, mask
        return None, None

def create_chart(chart_data: pd.DataFrame, display_swing_highs: pd.Series, 
                display_swing_lows: pd.Series, fib_levels: dict, 
                ticker: str, view_text: str, level_mode: str) -> go.Figure:
    fig = go.Figure()
    
    # Add candlestick chart
    fig.add_trace(go.Candlestick(
        x=chart_data.index, open=chart_data['Open'],
        high=chart_data['High'], low=chart_data['Low'],
        close=chart_data['Close'], name='Price'
    ))
    
    # Add swing points
    fig.add_trace(go.Scatter(
        x=display_swing_highs.index, y=display_swing_highs,
        mode='markers', name='Swing Highs',
        marker=dict(size=10, color='red', symbol='triangle-down')
    ))
    
    fig.add_trace(go.Scatter(
        x=display_swing_lows.index, y=display_swing_lows,
        mode='markers', name='Swing Lows',
        marker=dict(size=10, color='green', symbol='triangle-up')
    ))
    
    # Filter levels based on mode
    if level_mode == "Key Levels (High, 0.500, Low)":
        display_levels = {k: v for k, v in fib_levels.items() if k in ['High', '0.500', 'Low']}
    else:
        display_levels = fib_levels
    
    # Add Fibonacci levels
    colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'violet']
    for (level, price), color in zip(display_levels.items(), colors):
        fig.add_hline(y=price, line_color=color, line_dash="dash",
                     annotation_text=f"{level}: {price:.2f}")   
    
    fig.update_layout(
        title=f'Fibonacci Analysis for {ticker} {view_text}',
        yaxis_title='Price', xaxis_title='Date'
    )
    
    return fig

def setup_sidebar_controls() -> tuple:
    window = st.sidebar.slider("Swing Point Window", 5, 20, 10)
    view_mode = st.sidebar.radio("View Mode", ["Full Period", "Recent Swings"], index=1)
    level_mode = st.sidebar.radio("Fibonacci Levels", ["All Levels", "Key Levels (High, 0.500, Low)"])
    num_swings = None
    if view_mode == "Recent Swings":
        num_swings = st.sidebar.slider("Number of Recent Swings", 3, 10, 5)
    return window, view_mode, num_swings, level_mode

def show_fibonacci_analysis(ticker: str, timeframe: str):
    interval, period = TIMEFRAMES.get(timeframe, ('1d', '6mo'))
    data = fetch_stock_data(ticker, period=period, interval=interval)
    
    if data is None:
        st.error(f"No data available for {ticker}")
        return

    # Setup controls
    window, view_mode, num_swings, level_mode = setup_sidebar_controls()
    
    # Initialize analysis
    fib_analysis = FibonacciAnalysis(data)
    swing_highs, swing_lows = identify_swing_points(data, window)
    
    # Process data based on view mode
    if view_mode == "Recent Swings":
        display_data = process_recent_view(fib_analysis, swing_highs, swing_lows, 
                                         num_swings, data)
    else:
        display_data = process_full_view(swing_highs, swing_lows, data)
    
    if display_data is None:
        return
        
    # Create and display visualization
    chart_data, display_swing_highs, display_swing_lows, fib_levels = display_data
    view_text = f"({view_mode})" if view_mode == "Full Period" else f"(Last {num_swings} swings)"
    
    fig = create_chart(chart_data, display_swing_highs, display_swing_lows, 
                      fib_levels, ticker, view_text, level_mode)
    st.plotly_chart(fig)
    
    # Display levels table with filtered levels
    st.write("Fibonacci Levels (based on last swing points):")
    if level_mode == "Key Levels (High, 0.500, Low)":
        display_levels = {k: v for k, v in fib_levels.items() if k in ['High', '0.500', 'Low']}
    else:
        display_levels = fib_levels
    st.dataframe(pd.DataFrame.from_dict(display_levels, orient='index',
                                      columns=['Price Level']))

def process_recent_view(fib_analysis, swing_highs, swing_lows, num_swings, data):
    recent_highs, mask_highs = fib_analysis.get_recent_swings(swing_highs, num_swings)
    recent_lows, mask_lows = fib_analysis.get_recent_swings(swing_lows, num_swings)
    
    if recent_highs is None or recent_lows is None:
        st.warning("Not enough swing points for recent view")
        return None
    
    mask = mask_highs | mask_lows
    chart_data = data[mask]
    return process_swing_data(chart_data, recent_highs, recent_lows, fib_analysis)

def process_full_view(swing_highs, swing_lows, data):
    display_swing_highs = swing_highs.dropna()
    display_swing_lows = swing_lows.dropna()
    return process_swing_data(data, display_swing_highs, display_swing_lows, 
                            FibonacciAnalysis(data))

def process_swing_data(chart_data, display_swing_highs, display_swing_lows, fib_analysis):
    if display_swing_highs.empty or display_swing_lows.empty:
        st.warning("No valid swing points found in the selected timeframe")
        return None
    
    last_swing_high = display_swing_highs.iloc[-1]
    last_swing_low = display_swing_lows.iloc[-1]
    fib_levels = fib_analysis.calculate_fibonacci_levels(last_swing_high, last_swing_low)
    
    return chart_data, display_swing_highs, display_swing_lows, fib_levels
