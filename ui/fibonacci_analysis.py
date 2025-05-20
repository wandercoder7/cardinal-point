import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.data_fetching import fetch_stock_data
from utils.constants import TIMEFRAMES

def calculate_fibonacci_levels(data):
    highest_high = data['High'].max()
    lowest_low = data['Low'].min()
    price_range = highest_high - lowest_low
    
    levels = {
        'High': highest_high,
        'Low': lowest_low,
        '0.236': lowest_low + (price_range * 0.236),
        '0.382': lowest_low + (price_range * 0.382),
        '0.500': lowest_low + (price_range * 0.500),
        '0.618': lowest_low + (price_range * 0.618),
        '0.786': lowest_low + (price_range * 0.786),
    }
    return levels

def show_fibonacci_analysis(ticker, timeframe):
    interval, period = TIMEFRAMES.get(timeframe, ('1d', '6mo'))
    data = fetch_stock_data(ticker, period=period, interval=interval)
    
    if data is None:
        st.error(f"No data available for {ticker}")
        return
        
    fib_levels = calculate_fibonacci_levels(data)
    
    fig = go.Figure()
    
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name='Price'
    ))
    
    colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'violet']
    for (level, price), color in zip(fib_levels.items(), colors):
        fig.add_hline(y=price, line_color=color, line_dash="dash", 
                     annotation_text=f"{level}: {price:.2f}")
    
    fig.update_layout(
        title=f'Fibonacci Analysis for {ticker} ({timeframe})',
        yaxis_title='Price',
        xaxis_title='Date'
    )
    
    st.plotly_chart(fig)
    
    st.write("Fibonacci Levels:")
    st.dataframe(pd.DataFrame.from_dict(fib_levels, orient='index', 
                                      columns=['Price Level']))
