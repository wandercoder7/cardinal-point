from nsepy import get_index_pe_history
from datetime import date
import pandas as pd

nifty_50_tickers_yfinance = [
    "ADANIENT.NS",
    "ADANIPORTS.NS",
    "APOLLOHOSP.NS",
    "ASIANPAINT.NS",
    "AXISBANK.NS",
    "BAJAJ-AUTO.NS",
    "BAJFINANCE.NS",
    "BAJAJFINSV.NS",
    "BHARATFORG.NS",  # Assuming Bharat Forge as BEL is a PSU
    "BHARTIARTL.NS",
    "CIPLA.NS",
    "COALINDIA.NS",
    "DRREDDY.NS",
    "EICHERMOT.NS",
    "GRASIM.NS",
    "HCLTECH.NS",
    "HDFCBANK.NS",
    "HDFCLIFE.NS",
    "HEROMOTOCO.NS",
    "HINDALCO.NS",
    "HINDUNILVR.NS",
    "ICICIBANK.NS",
    "INDUSINDBK.NS",
    "INFY.NS",
    "ITC.NS",
    "JSWSTEEL.NS",
    "KOTAKBANK.NS",
    "LT.NS",
    "M&M.NS",
    "MARUTI.NS",
    "NESTLEIND.NS",
    "NTPC.NS",
    "ONGC.NS",
    "POWERGRID.NS",
    "RELIANCE.NS",
    "SBILIFE.NS",
    "SBIN.NS",
    "SUNPHARMA.NS",
    "TATACONSUM.NS",
    "TATAMOTORS.NS",
    "TATASTEEL.NS",
    "TCS.NS",
    "TECHM.NS",
    "TITAN.NS",
    "ULTRACEMCO.NS",
    "UPL.NS",
    "WIPRO.NS",
    "SHRIRAMFIN.NS"
]

def get_nifty500_symbols():
    try:
        # Get Nifty 500 constituents using nsepy
        nifty500 = get_index_pe_history(symbol="NIFTY 500",
                                      start=date.today(),
                                      end=date.today())
        
        # Convert index symbols to yfinance format
        symbols = [f"{stock}.NS" for stock in nifty500.index]
        return symbols
    except Exception as e:
        print(f"Error fetching Nifty 500 symbols: {e}")
        return []

# Use this function to get the latest Nifty 500 symbols
nifty_500_tickers_yfinance = get_nifty500_symbols()