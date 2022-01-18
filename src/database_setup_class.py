import sqlalchemy
import sqlite3
import pathlib
import pandas as pd
import yfinance as yf

from typing import List

MAIN_DIRECTORY_PATH = pathlib.Path(__file__).parent.parent.resolve()
DATA_DIRECTORY_PATH = f"{MAIN_DIRECTORY_PATH}/data"


class Database:
    def __init__(self, database_name: str) -> None:
        self.database_name = database_name
        self.engine = sqlalchemy.create_engine(
            f"sqlite:///{DATA_DIRECTORY_PATH}/{self.database_name}.db"
        )
        self.index = database_name
        
        self.ticker_list = []

    def get_ticker_symbols(self) -> List:
        # Hard code to get the list of ticker symbols for a few indices
        # Indices will be using
        # DowJones (DJIA), NIFTY50

        if self.index == "DJIA":
            ticker_list = pd.read_html(
                f"https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average"
            )[1]["Symbol"].to_list()

        elif self.index == "NIFTY50":
            ticker_list = pd.read_html("https://en.wikipedia.org/wiki/NIFTY_50")[1][
                "Symbol"
            ].to_list()
            ticker_list = [f"{ticker}.NS" for ticker in ticker_list]

        self.ticker_list = ticker_list
        return ticker_list

    
    def download_stock_data(
        self, ticker_symbol: str, start: str = "2020-01-01"
    ) -> pd.DataFrame:

        df = yf.download(ticker_symbol, start)
        df = df.reset_index()
        return df

    def add_stock_data_to_database(
        self, if_exists: str = "fail", start: str = "2020-01-01"
    ) -> None:
        ticker_list = self.get_ticker_symbols()
        stock_data = [
            self.download_stock_data(ticker_symbol, start=start)
            for ticker_symbol in ticker_list
        ]
        for ticker, data_frame in zip(ticker_list, stock_data):
            data_frame.to_sql(ticker.split(".")[0], self.engine, if_exists=if_exists)

    def get_max_date(self):
        query = f"SELECT name FROM sqlite_master WHERE type='table'"
        df = pd.read_sql(query, self.engine)

        query = f"SELECT MAX(Date) FROM {df['name'][0]}"
        max_date = pd.read_sql(query, self.engine)
        max_date = max_date["MAX(Date)"][0].split(" ")[0]
        return max_date

    def update(self):

        max_date = self.get_max_date()
        ticker_list = self.get_ticker_symbols()

        for ticker_symbol in ticker_list:

            stock_frame = yf.download(ticker_symbol, start=max_date)
            stock_frame = stock_frame[stock_frame.index > max_date]
            stock_frame = stock_frame.reset_index()
            stock_frame.to_sql(
                ticker_symbol.split(".")[0], self.engine, if_exists="append"
            )

        print(f"{self.index} successfully updated")
