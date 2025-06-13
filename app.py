import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("📈 Real-Time VWAP + JMA Chart Viewer")

# User Input
tickers = st.multiselect("Select stock tickers", 
                         ["TSLA", "APLD", "QBTS", "SBET", "DFDV", 
                          "TSLL", "SOXL", "CHYM", "SOFI", "BBAI", 
                          "HIMS", "IONQ"], default=["TSLA"])

for ticker in tickers:
    st.subheader(f"{ticker} Chart")
    
    # Using 5-minute interval for better data availability on Streamlit Cloud
    data = yf.download(ticker, period="5d", interval="5m")

    if data.empty or 'Volume' not in data.columns:
        st.warning(f"No sufficient data available for {ticker}. Try a different one.")
        continue  # Move to the next ticker

    # Calculate indicators
    data['Typical_Price'] = (data['High'] + data['Low'] + data['Close']) / 3
    data['TPV'] = data['Typical_Price'] * data['Volume']
    data['VWAP'] = data['TPV'].cumsum() / data['Volume'].cumsum()
    data['JMA'] = data['Close'].ewm(span=10, adjust=False).mean().ewm(span=5, adjust=False).mean()

    # Plot
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(data.index, data['Close'], label='Close Price', linestyle='--')
    ax.plot(data.index, data['VWAP'], label='VWAP', linewidth=2)
    ax.plot(data.index, data['JMA'], label='JMA', linewidth=2)
    ax.set_title(f"{ticker} - VWAP & JMA")
    ax.set_xlabel("Time")
    ax.set_ylabel("Price")
    ax.grid(True)
    ax.legend()
    st.pyplot(fig)
