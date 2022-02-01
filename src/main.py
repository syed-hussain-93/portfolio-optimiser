import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go


from assets_class import Asset
from portfolio_class import Portfolio
from database_setup_class import Database




def yf_retrieve_data(ticker_list, date_range):
    data_frames = []
    for ticker in ticker_list:
        data = yf.download(ticker, start=date_range[0], end=date_range[1])
        data_frames.append(data)
    return data_frames

@st.cache
def run_optimiser(portfolio,optimiser, usr_input=None):
    return portfolio.run_optimisation(optimiser,usr_input=usr_input)

@st.cache
def run_efficient_frontier(portfolio):
    df = pd.DataFrame(portfolio.efficient_frontier())
    df.rename = ["Volatility", "Returns"]
    return df
    
    

def main():
    
    dow_jones_db = Database("DJIA")

    st.title("Portfolio Optimiser")

    menu = ["Home", "Explore"]
    choice = st.sidebar.selectbox("Select Page", menu)

    if choice == "Home":
        st.subheader("Optimise Portfolio")

        ticker_list = dow_jones_db.get_ticker_list()
        selected_assets = st.multiselect("Pick your assets", ticker_list)

        if selected_assets:
            assets = []
            for ticker in selected_assets:
                sql_query = f"SELECT * FROM `{ticker}`"
                data = pd.read_sql(sql_query,dow_jones_db.engine)
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
                    results = run_optimiser(portfolio, opt, usr_input=usr_input)
                    # results = portfolio.run_optimisation(opt, usr_input=usr_input)

                    portfolio_returns.append(results["returns"])
                    portfolio_stds.append(results["std"])
                    portfolio_weights.append(results["weights"])

                volatility_returns_df = pd.DataFrame.from_dict(
                    {"Return": portfolio_returns, "Volatility": portfolio_stds},
                    orient="index",
                    columns=selected_optimisation,
                )
                
                volatility_returns_df = volatility_returns_df.transpose()
                
                st.subheader("Asset Weights")
                weights_df = pd.DataFrame(portfolio_weights)
                weights_df.index = selected_optimisation
                weights_df.columns = selected_assets

                st.write(weights_df)
                st.bar_chart(weights_df)

                st.subheader("Portfolio Return and Volatility")
                st.write(volatility_returns_df)
                st.bar_chart(volatility_returns_df["Return"])

            # efficient frontier
            st.subheader("Plot Efficient Frontier")
            ef = st.checkbox("Show Efficient Frontier")
            
            
            
            if ef:
                results = run_efficient_frontier(portfolio)
                # results = portfolio.efficient_frontier()
                # volatility = results["std"]
                # returns = results["returns"]
                fig = go.Figure()
                
                fig.add_trace(
                    go.Line(
                        x=results.iloc[:,0],
                        y=results.iloc[:,1],
                        name="Efficient Frontier"
                    )
                )
                
                if selected_optimisation:
                    for opt in selected_optimisation:
                        X = volatility_returns_df.loc[opt,"Volatility"]
                        Y= volatility_returns_df.loc[opt,"Return"]
                        fig.add_trace(
                            go.Scatter(
                                x = [X],
                                y=[Y],
                                name=opt
                            )
                        )
                
                fig.update_layout(
                    title="Returns Vs Volatility",
                    xaxis_title="Volatility",
                    yaxis_title="Returns",
                    legend_title="Legend"
                )
                
                # fig = px.line(
                #     data_frame = results,
                #     x=results.columns[0],
                #     y=results.columns[1],
                #     title="Efficient Frontier"
                #               )
                
                
                st.plotly_chart(fig)
    else:
        st.subheader("Explore")

        start = st.date_input("Start", value=pd.to_datetime("2010-01-01"))
        end = st.date_input("End", value=pd.to_datetime("today"))


if __name__ == "__main__":
    main()
