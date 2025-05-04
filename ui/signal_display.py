import streamlit as st
import pandas as pd

def display_signals_table(signals_df: pd.DataFrame, timeframes: list):
    st.subheader("Tickers with Breakout Signals:")
    
    # Extract all possible signals from the dataframe columns
    signal_columns = [col for col in signals_df.columns if 'Signals' in col]
    all_signals = set()
    for col in signal_columns:
        # Split signal strings and add individual signals to the set
        signals = [signal.strip() for signals_list in signals_df[col].dropna() 
                  for signal in signals_list.split(',') if signal.strip() != 'No Signal']
        all_signals.update(signals)
    
    # Create a multi-select filter for signals
    selected_signals = st.multiselect(
        "Filter by Signals:",
        sorted(list(all_signals)),
        default=[]
    )
    
    # Filter the dataframe based on selected signals
    if selected_signals:
        mask = pd.Series(False, index=signals_df.index)
        for col in signal_columns:
            for signal in selected_signals:
                mask |= signals_df[col].str.contains(signal, na=False)
        filtered_df = signals_df[mask]
    else:
        filtered_df = signals_df

    # Display the filtered dataframe
    if filtered_df.empty:
        st.info("No tickers match the selected signal filters.")
    else:
        st.dataframe(filtered_df)

    all_tickers = [""] + filtered_df['Ticker'].tolist()
    selected_ticker = st.selectbox("Select a ticker to view its chart:", all_tickers)
    selected_timeframe = None
    if selected_ticker:
        timeframe_options = [""] + timeframes
        selected_timeframe = st.selectbox("Select a timeframe for the chart:", timeframe_options)
        if selected_timeframe:
            return (selected_ticker, selected_timeframe)
    return (None, None)