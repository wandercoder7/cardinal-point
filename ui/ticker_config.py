import streamlit as st
import pandas as pd
from utils.constants import get_all_tickers, save_tickers, DEFAULT_TICKERS

def show_ticker_configuration():
    st.title("Ticker Configuration")
    
    # Display current tickers
    current_tickers = get_all_tickers()
    st.subheader("Current Tickers")
    
    # Convert tickers to DataFrame for better display
    df = pd.DataFrame(current_tickers, columns=['Symbol'])
    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        column_config={
            "Symbol": st.column_config.TextColumn(
                "Symbol",
                help="Stock symbol with .NS suffix for NSE stocks",
                max_chars=20,
                validate="^[A-Z0-9&-]+\.NS$"
            )
        }
    )
    
    # Save button
    if st.button("Save Changes"):
        new_tickers = edited_df['Symbol'].tolist()
        save_tickers(new_tickers)
        st.success("Ticker configuration saved successfully!")
    
    # Reset button
    if st.button("Reset to Default"):
        save_tickers(DEFAULT_TICKERS)
        st.success("Tickers reset to default configuration!")
        st.rerun()
