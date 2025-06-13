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

    data = yf.download(ticker, period="5d", interval="5m", progress=False)

    # Find which required columns exist
    available_columns = [col for col in required_columns if col in data.columns]

    # If key columns missing, skip
    if data.empty or len(available_columns) < len(required_columns):
        st.warning(f"{ticker}: Missing essential columns. Skipping.")
        continue

    # Drop rows with missing values only for available columns
    data = data.dropna(subset=available_columns)

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
