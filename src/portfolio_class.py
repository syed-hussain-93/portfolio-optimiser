from typing import List, Optional, Tuple
from unittest import result
from assets_class import Asset
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from functools import lru_cache

RISK_FREE_RATE = 1.3  # UK 2021


class Portfolio:
    def __init__(self, assets: List) -> None:

        self.assets = assets        
        self.size = len(self.assets)
        self.data_dates = assets[0].data['Date']
        
        self.weights = []
    
    @lru_cache    
    def assets_close_price_data(self, date:bool = None):
        portfolio_data = pd.concat(
            [asset.data["Close"] for asset in self.assets], axis=1
        )
        portfolio_data.columns = [asset.name for asset in self.assets]
        if date:
            portfolio_data.insert(loc=0, column='Date', value=self.data_dates)
        portfolio_data = portfolio_data.dropna()
        return portfolio_data
    
    @lru_cache
    def assets_returns_data(self, date: bool=False):
        assets_returns = pd.concat(
            [asset.return_prices() for asset in self.assets], axis=1
        )
        assets_returns.columns = [asset.name for asset in self.assets]
        if date:
            assets_returns.insert(loc=0, column='Date', value=self.data_dates)
        assets_returns = assets_returns.dropna()
        return assets_returns
    
    @lru_cache
    def assets_mean_annualised_returns(self):
        annualised_returns = [asset.mean_returns() for asset in self.assets]
        return annualised_returns
    
    def set_random_weights(self):

        weights = np.random.random(self.size)
        weights /= np.sum(weights)

        # self.weights = weights
        return weights

    def _portfolio_return(self, weights):
        # Annual expected portoflio return
        return np.dot(weights, self.assets_mean_annualised_returns())

    def portfolio_expected_return(self, weights):
        
        return self._portfolio_return(weights)

    @lru_cache
    def covariance_matrix(self, period="annual", frequency=250):
        daily_cov_matrix = self.assets_returns_data().cov()
        return frequency * daily_cov_matrix

    def _portfolio_std(self, weights: List):
        variance = np.dot(weights, np.dot(self.covariance_matrix(), weights))
        return np.sqrt(variance)

    def portfolio_std(self,weights):
        return self._portfolio_std(weights)

    def monte_carlo(self, iterations=1000):

        returns = []
        stds = []
        weights_list = []

        for i in range(iterations):
            weights = self.set_random_weights()
            returns.append(self._portfolio_return(weights))
            stds.append(self._portfolio_std(weights))
            weights_list.append(weights)

        return returns, stds, weights

    def optimise_with_risk_tolerance(self, risk_tolerance: float):

        result = minimize(
            lambda w: self._portfolio_std(w)
            - risk_tolerance * self._portfolio_return(w),
            self.set_random_weights(),
            constraints=[{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}],
            bounds=[(0.0, 1.0) for i in range(self.size)],
        )
        weights = result.x
        return weights

    def optimise_sharpe_ratio(self):

        result = minimize(
            lambda w: -np.divide(
                (self._portfolio_return(w) - RISK_FREE_RATE / 100),
                self._portfolio_std(w),
            ),
            self.set_random_weights(),
            constraints=[{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}],
            bounds=[(0.0, 1.0) for i in range(self.size)],
        )
        return result.x

    def optimise_with_expected_return(self, expected_return: float):

        result = minimize(
            lambda w: self._portfolio_std(w),
            self.set_random_weights(),
            constraints=[
                {"type": "eq", "fun": lambda w: np.sum(w) - 1.0},
                {
                    "type": "eq",
                    "fun": lambda w: self._portfolio_std(w) - expected_return,
                },
            ],
            bounds=[(0.0, 1.0) for i in range(self.size)],
        )
        return result.x
    
    @lru_cache
    def efficient_frontier(self):
        
        # Drawing the efficient frontier
        volatility = []
        returns = []
        for rt in np.linspace(-500, 500, 2000):
            weights = self.optimise_with_risk_tolerance(rt)
            volatility.append(self.portfolio_std(weights))
            returns.append(self.portfolio_expected_return(weights))
        
        results = {"std": volatility, "returns": returns}
        return results

    def run_optimisation(self, opt: str, usr_input: float = None) -> None:
        if opt == "Risk Tolerance":
            weights = self.optimise_with_risk_tolerance(risk_tolerance=usr_input)
        elif opt == "Expect Return":
            weights = self.optimise_with_expected_return(expected_return=usr_input)
        elif opt == "Sharpe Ratio":
            weights = self.optimise_sharpe_ratio()
        elif opt == "Risk Free":
            weights = self.optimise_with_risk_tolerance(risk_tolerance=0.0)

        results = {"weights": weights, "returns": self.portfolio_expected_return(weights), "std": self.portfolio_std(weights)}
        
        return results