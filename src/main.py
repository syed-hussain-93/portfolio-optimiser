import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt


from assets_class import Asset
from portfolio_class import Portfolio


def yf_retrieve_data(ticker_list, date_range):
    data_frames = []
    for ticker in ticker_list:
        data = yf.download(ticker, start=date_range[0], end=date_range[1])
        data_frames.append(data)
    return data_frames


def main():
    st.title("Portfolio Optimiser")

    menu = ["Home", "Explore"]
    choice = st.sidebar.selectbox("Select Page", menu)

    if choice == "Home":
        st.subheader("Optimise Portfolio")

        ticker_list = ("AAPL", "FB", "AMZN", "NFLX", "GOOG")
        dropdown = st.multiselect("Pick your assets", ticker_list)

        start = st.date_input("Start", value=pd.to_datetime("2010-01-01"))
        end = st.date_input("End", value=pd.to_datetime("today"))

    else:
        st.subheader("Explore")


if __name__ == "__main__":
    main()
