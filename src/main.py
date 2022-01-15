from assets_class import Asset
from portfolio_class import Portfolio
from datetime import datetime
import numpy as np
import pandas as pd
date_range = ["2013-01-01", datetime.today().strftime('%Y-%m-%d')]
ticker_list = ["AAPL", "FB", "AMZN", "NFLX", "GOOG"]

# portfolio = Portfolio([Asset({"ticker": ticker, "date_range": date_range}) for ticker in ticker_list])
portfolio = Portfolio(ticker_list, date_range=date_range)

portfolio_dataframe = portfolio.get_dataframe()

test_asset = Asset({"ticker": "FB", "date_range": date_range})

