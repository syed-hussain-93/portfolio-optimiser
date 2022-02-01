from typing import Dict, List
from pandas_datareader import data as web


import pandas as pd
import numpy as np


TRADING_DAYS_PER_YEAR = 250


class Asset:
    def __init__(self, stock: dict):

        self.name = stock["name"]
        self.data = stock["data"]

        # Daily log returns
        # self.daily_returns = self.data.loc[:,'Close'].pct_change().apply(lambda x: np.log(1 + x))
        
        # Expected daily returns
        # self.expected_daily_return = np.mean(self.daily_returns)

        # self.data = pd.DataFrame()
        # self.data[self.name] = web.DataReader(self.name, data_source='yahoo', start= self.start_date, end= self.end_date)['Close']
        
    
    def return_prices(self) -> pd.DataFrame:
        """
        Calculate the daily log returns for asset as a data frame
        """        
        return self.data.loc[:,'Close'].pct_change().apply(lambda x: np.log(1 + x))


    def mean_returns(self, frequency: int =250) -> list:
        """"
        Calculate annualised mean (log) returns
        
        """
        return self.return_prices().mean() * frequency
    
    
    def ema(self, span=50):
        """
        Calculate exponential moving average of historical daily returns
        
        """
    
    def stock_beta(self, market_daily_returns: pd.DataFrame):
        cov = self.return_prices().cov(market_daily_returns)
        market_variance = market_daily_returns.var()
        beta = cov/market_variance
        return beta
    
    def capm_return(self):
        
        
        
        pass

    def __repr__(self):
        return f"<Asset name={self.name}, expected annualised log return={self.mean_returns()}>"
