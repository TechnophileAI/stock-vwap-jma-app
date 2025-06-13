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

required_columns = ["high", "low", "close", "volume"]

for ticker in tickers:
    st.subheader(f"{ticker} Chart")

    # Force grouped output
    data = yf.download([ticker], period="2d", interval="1m", group_by="ticker", progress=False)

    # Handle grouped DataFrame
    if isinstance(data.columns, pd.MultiIndex):
        try:
            data = data[ticker]  # Extract only the sub-DataFrame for that ticker
            data.columns = [col.lower() for col in data.columns]
        except KeyError:
            st.warning(f"{ticker}: No data returned or structure issue.")
            continue
    else:
        data.columns = [col.lower() for col in data.columns]

    st.text(f"{ticker} columns: {list(data.columns)}")

    if data.empty or not all(col in data.columns for col in required_columns):
        st.warning(f"{ticker}: Required columns missing. Skipping.")
        continue

    data = data.dropna(subset=required_columns)

    # Calculate indicators
    data['typical_price'] = (data['high'] + data['low'] + data['close']) / 3
    data['tpv'] = data['typical_price'] * data['volume']
    data['vwap'] = data['tpv'].cumsum() / data['volume'].cumsum()
    data['jma'] = data['close'].ewm(span=10, adjust=False).mean().ewm(span=5, adjust=False).mean()

    # Plot chart
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(data.index, data['close'], label='Close Price', linestyle='--')
    ax.plot(data.index, data['vwap'], label='VWAP', linewidth=2)
    ax.plot(data.index, data['jma'], label='JMA', linewidth=2)
    ax.set_title(f"{ticker} - VWAP & JMA")
    ax.set_xlabel("Time")
    ax.set_ylabel("Price")
    ax.grid(True)
    ax.legend()
    st.pyplot(fig)
