from typing import List, Optional, Tuple
from assets_class import Asset
import numpy as np
import pandas as pd
from scipy.optimize import minimize


TRADING_DAYS_PER_YEAR = 250
RISK_FREE_RATE = 0.11  # 1.3  # UK 2021


class Portfolio:
    def __init__(self, assets: List = []) -> None:

        self.assets = assets

        self.portfolio_data = pd.concat(
            [asset.data["Close"] for asset in self.assets], axis=1
        ).dropna()
        self.portfolio_data.columns = [asset.name for asset in self.assets]

        self.assets_daily_returns = pd.concat(
            [asset.daily_returns for asset in self.assets], axis=1
        ).dropna()
        self.size = len(self.assets)

        self.weights = []

    def set_random_weights(self):

        weights = np.random.random(self.size)
        weights /= np.sum(weights)

        self.weights = weights
        return self.weights

    def _portfolio_return(self, weights: List):
        # Annual expected portoflio return
        daily = np.dot(weights, self.assets_daily_returns.mean())
        return TRADING_DAYS_PER_YEAR * daily

    @property
    def portfolio_expected_return(self):
        return self._portfolio_return(self.weights)

    def covariance_matrix(self, period="annual"):
        daily_cov_matrix = self.assets_daily_returns.cov()
        return TRADING_DAYS_PER_YEAR * daily_cov_matrix

    def _portfolio_std(self, weights: List):
        variance = np.dot(weights, np.dot(self.covariance_matrix(), weights))
        return np.sqrt(variance)

    @property
    def portfolio_std(self):
        return self._portfolio_std(self.weights)

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

        self.weights = result.x

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
        self.weights = result.x

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
        self.weights = result.x

    def run_optimisation(self, opt: str, usr_input: float = None) -> None:
        if opt == "Risk Tolerance":
            self.optimise_with_risk_tolerance(risk_tolerance=usr_input)
        elif opt == "Expect Return":
            self.optimise_with_expected_return(expected_return=usr_input)
        elif opt == "Sharpe Ratio":
            self.optimise_sharpe_ratio()
        elif opt == "Risk Free":
            self.optimise_with_risk_tolerance(risk_tolerance=0.0)
