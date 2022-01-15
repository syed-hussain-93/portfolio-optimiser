from typing import Dict
from pandas_datareader import data as web
import pandas as pd
from datetime import datetime
from dateutil import relativedelta

import numpy as np


TRADING_DAYS_PER_YEAR = 250

class Asset:
    
    def __init__(self, stock: dict):
        
        self.name = stock["name"]
        self.data = stock["data"]
                
        # Daily log returns
        self.daily_returns = self.data['Close'].pct_change().apply(lambda x: np.log(1+x)).dropna()
        # Expected daily returns
        self.expected_daily_return = np.mean(self.daily_returns)
        
        # self.data = pd.DataFrame()
        # self.data[self.name] = web.DataReader(self.name, data_source='yahoo', start= self.start_date, end= self.end_date)['Close']
    
    def annual_returns(self) -> pd.DataFrame:
        
        return self.expected_daily_return * TRADING_DAYS_PER_YEAR
    
    def __repr__(self):
        return f'<Asset name={self.name}, expected return={self.expected_daily_return}>'
    
