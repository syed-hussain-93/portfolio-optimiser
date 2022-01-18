import streamlit as st
import yfinance as yf
import pandas as pd


from assets_class import Asset
from portfolio_class import Portfolio
from database_setup_class import Database


def yf_retrieve_data(ticker_list, date_range):
    data_frames = []
    for ticker in ticker_list:
        data = yf.download(ticker, start=date_range[0], end=date_range[1])
        data_frames.append(data)
    return data_frames


def main():
    dow_jones_db = Database("DJIA")

    st.title("Portfolio Optimiser")

    menu = ["Home", "Explore"]
    choice = st.sidebar.selectbox("Select Page", menu)

    if choice == "Home":
        st.subheader("Optimise Portfolio")

        ticker_list = dow_jones_db.get_ticker_symbols()
        selected_assets = st.multiselect("Pick your assets", ticker_list)

        if selected_assets:
            assets = []
            for ticker in selected_assets:
                sql_query = f"SELECT * FROM {ticker}"
                data = pd.read_sql(sql_query, dow_jones_db.engine)
                assets.append(Asset({"name": ticker, "data": data}))

            portfolio = Portfolio(assets)

            selected_optimisation = st.multiselect(
                "Choose optimisation",
                ["Risk Free", "Risk Tolerance", "Expect Return", "Sharpe Ratio"],
            )

            if selected_optimisation:

                portfolio_returns = []
                portfolio_stds = []
                portfolio_weights = []
                for opt in selected_optimisation:

                    if opt == "Risk Tolerance":
                        usr_input = st.number_input("Enter Risk Tolerance: ", 0.0)
                    elif opt == "Expect Return":
                        usr_input = st.number_input(
                            "Enter what percentage you would like to see a return of: ",
                            25,
                            max_value=100,
                        )
                        usr_input = usr_input / 100
                    else:
                        usr_input = None
                    portfolio.run_optimisation(opt, usr_input=usr_input)

                    portfolio_returns.append(portfolio.portfolio_expected_return)
                    portfolio_stds.append(portfolio.portfolio_std)
                    portfolio_weights.append(portfolio.weights)

                volatility_returns_df = pd.DataFrame.from_dict(
                    {"Return": portfolio_returns, "Volatility": portfolio_stds},
                    orient="index",
                    columns=selected_optimisation,
                )
                st.subheader("Asset Weights")
                weights_df = pd.DataFrame(portfolio_weights)
                weights_df.index = selected_optimisation
                weights_df.columns = selected_assets

                st.write(weights_df)
                st.bar_chart(weights_df)

                st.subheader("Portfolio Return and Volatility")
                st.write(volatility_returns_df.transpose())
                st.bar_chart(volatility_returns_df.transpose()["Return"])

                st.text("$1000 USD will return: ")
                volatility_returns_df2 = volatility_returns_df.copy()
                volatility_returns_df2.iloc[0, :] = [
                    round((r + 1) * 1000) for r in volatility_returns_df2.iloc[0, :]
                ]
                st.write(volatility_returns_df2.iloc[0, :])

    else:
        st.subheader("Explore")

        start = st.date_input("Start", value=pd.to_datetime("2010-01-01"))
        end = st.date_input("End", value=pd.to_datetime("today"))


if __name__ == "__main__":
    main()
