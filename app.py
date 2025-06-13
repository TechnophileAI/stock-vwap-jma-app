import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("📈 Real-Time VWAP + JMA Chart Viewer")

tickers = st.multiselect("Select stock tickers", 
                         ["TSLA", "APLD", "QBTS", "SBET", "DFDV", 
                          "TSLL", "SOXL", "CHYM", "SOFI", "BBAI", 
                          "HIMS", "IONQ"], default=["TSLA"])

required_columns = ["High", "Low", "Close", "Volume"]

for ticker in tickers:
    st.subheader(f"{ticker} Chart")

    # Fetch data
    data = yf.download(ticker, period="5d", interval="5m", progress=False)

    # Normalize column names (ensure consistent format)
    data.columns = [col.title() for col in data.columns]

    # Check if all required columns exist
    if data.empty or not all(col in data.columns for col in required_columns):
        st.warning(f"{ticker}: Required columns missing from data. Skipping.")
        continue

    # Drop rows with NaNs in required columns
    try:
        data = data.dropna(subset=required_columns)
    except KeyError:
        st.warning(f"{ticker}: Unable to drop NaNs due to missing columns. Skipping.")
        continue

    # Calculate indicators
    data['Typical_Price'] = (data['High'] + data['Low'] + data['Close']) / 3
    data['TPV'] = data['Typical_Price'] * data['Volume']
    data['VWAP'] = data['TPV'].cumsum() / data['Volume'].cumsum()
    data['JMA'] = data['Close'].ewm(span=10, adjust=False).mean().ewm(span=5, adjust=False).mean()

    # Plotting
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
