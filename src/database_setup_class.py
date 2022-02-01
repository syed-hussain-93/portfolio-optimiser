from queue import Empty
import sqlalchemy
import pathlib
import pandas as pd
import yfinance as yf

    
from datetime import datetime
from typing import Dict, List

MAIN_DIRECTORY_PATH = pathlib.Path(__file__).parent.parent.resolve()
DATA_DIRECTORY_PATH = f"{MAIN_DIRECTORY_PATH}/data"

def get_ticker_symbols(index) -> List:
    # Hard code to get the list of ticker symbols for a few indices
    # Indices will be using
    # DowJones (DJIA), NIFTY50

    if index == "DJIA":
        ticker_list = pd.read_html(
            f"https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average"
        )[1]["Symbol"].to_list()

    elif index == "NIFTY50":
        ticker_list = pd.read_html("https://en.wikipedia.org/wiki/NIFTY_50")[1][
            "Symbol"
        ].to_list()
        ticker_list = [f"{ticker}.NS" for ticker in ticker_list]

    return ticker_list

class Database:
    def __init__(self, database_name: str) -> None:
        self.database_name = database_name
        self.engine = sqlalchemy.create_engine(
            f"sqlite:///{DATA_DIRECTORY_PATH}/{self.database_name}.db"
        )

        self.max_date = datetime(1900,1,1).date()
        
    def _download_stock_data(
        self, ticker_symbol: str, start, end
    ) -> pd.DataFrame:

        df = yf.download(ticker_symbol, start,end)
        df = df.reset_index()
        return df

    def _single_stock(
        self, stock_ticker: str, start, end, if_exists='fail'
    ):
        stock_data = self._download_stock_data(stock_ticker, start = start, end=end)
        table_name = stock_ticker.split(".")[0]
        stock_data.to_sql(table_name, self.engine, if_exists=if_exists)    
    
        print(f"Sucessfully added {stock_ticker} to database")


    def get_stock_table_names(self):
        
        query = f"SELECT name FROM sqlite_master WHERE type='table'"
        df = pd.read_sql_query(query,self.engine)
        df = df[df["name"] != "tickers"]
        tables_names = df['name'].tolist()

        return tables_names
    
    def _add_ticker_list_to_database(self, ticker_list):

        tickers = pd.DataFrame(ticker_list, columns=['ticker'])
        tickers.to_sql('tickers', self.engine, if_exists='append')
        pass
    
    def get_ticker_list(self):
        query = f"SELECT * FROM tickers"
        return pd.read_sql(query, self.engine)['ticker'].tolist()
        

    def add_stock_to_database(
        self, stock_ticker, start, end, if_exists='fail'
    ):
        if type(stock_ticker) is str:
            stock_data = self._single_stock(stock_ticker, start, end)
            stock_ticker = [stock_ticker]
        elif type(stock_ticker) is list:
            stock_data = [self._single_stock(stock,start, end) for stock in stock_ticker ]
        
        self._add_ticker_list_to_database(stock_ticker)
        
    def _get_table_date(self, MAX_MIN:str, table):
        query = f"SELECT {MAX_MIN.upper()}(Date) FROM `{table}`"
        date = pd.read_sql(query, self.engine)[f'{MAX_MIN}(Date)'][0].split(" ")[0]
        date = datetime.strptime(date,'%Y-%m-%d').date()
        return date
        
    def _get_min_max_date(self, MAX_MIN: str = 'MAX'):
        # use the last table that was added to get max date 
        for table in self.get_stock_table_names():
            date = self._get_table_date(MAX_MIN,table)
            if date > self.max_date:
                self.max_date = date
    
        return self.max_date.strftime('%Y-%m-%d')
        

    def update_database(self):
        max_date = self._get_min_max_date('MAX')
        for ticker_symbol, table_name in zip(self.get_ticker_list(), self.get_stock_table_names()):

            stock_frame = yf.download(ticker_symbol, start=max_date, end=None)
            stock_frame = stock_frame[stock_frame.index > max_date]
            stock_frame = stock_frame.reset_index()
            stock_frame.to_sql(
                table_name, self.engine, if_exists="append"
            )

        print(f"{self.database_name} successfully updated")     

        pass
            
    def _clean_data_frame(self, data_frame:pd.DataFrame):
        # Clean date
        data_frame['Date'] = data_frame['Date'].apply(lambda x: x.split(" ")[0])
        # drop index olumns
        data_frame = data_frame.drop(labels='index', axis=1)
        return data_frame
    
    def read_stock_data(self, ticker: str):
        
        query = f"SELECT * FROM `{ticker}`"
        stock_data = pd.read_sql(query, self.engine)
        stock_data = self._clean_data_frame(stock_data)
        
        return stock_data
    
    def read_all_stocks_data(self, ticker_list):
        stocks_data = []
        for ticker in ticker_list:
            stock_data = self.read_stock_data(ticker)
            stocks_data.append(stock_data)
        return stocks_data
            

        
    # def read_database(self):
    #     query = f"SELECT name FROM sqlite_master WHERE type='table'"
    #     stock_data = []        
    #     for ticker in self.get_ticker_symbols():
    #         if date_range:
    #             query = f"SELECT * FROM {ticker} WHERE Date BETWEEN '{date_range[0]}' AND '{date_range[1]}'"
    #         else:
    #             query = f"SELECT * FROM {ticker}"
    #         stock = pd.read_sql(query, self.engine)
    #         stock['Date'] = stock['Date'].apply(lambda x: x.split(" ")[0])
    #         stock = stock.drop(labels='index', axis=1)
        
    #         stock_data.append(stock)
                
    #     return stock_data
        

    # def add_stock_data_to_database(
    #     self, if_exists: str = "fail", start: str = "2020-01-01"
    # ) -> None:
        
    #     ticker_list = self.get_ticker_symbols()
    #     stock_data = [
    #         self.download_stock_data(ticker_symbol, start=start)
    #         for ticker_symbol in ticker_list
    #     ]
    #     for ticker, data_frame in zip(ticker_list, stock_data):
    #         data_frame.to_sql(ticker.split(".")[0], self.engine, if_exists=if_exists)


    # def get_dataframe(self, ticker_list  date_range: List = None):
    #     query = f"SELECT name FROM sqlite_master WHERE type='table'"
    #     stock_data = []        
    #     for ticker in self.get_ticker_symbols():
    #         if date_range:
    #             query = f"SELECT * FROM {ticker} WHERE Date BETWEEN '{date_range[0]}' AND '{date_range[1]}'"
    #         else:
    #             query = f"SELECT * FROM {ticker}"
    #         stock = pd.read_sql(query, self.engine)
    #         stock['Date'] = stock['Date'].apply(lambda x: x.split(" ")[0])
    #         stock = stock.drop(labels='index', axis=1)
        
    #         stock_data.append(stock)
             
    #     return stock_data
    
    # def _get_min_max_date(self, MAX_MIN: str):
    #     query = f"SELECT name FROM sqlite_master WHERE type='table'"
    #     df = pd.read_sql(query, self.engine)
        
    #     query = f"SELECT {MAX_MIN}(Date) FROM {df['name'][0]}"
    #     max_date = pd.read_sql(query, self.engine)
    #     max_date = max_date[f"{MAX_MIN}(Date)"][0].split(" ")[0]
    #     return max_date

    # def get_max_date(self):
    #     return self._get_min_max_date('MAX')
    
    # def get_min_date(self):
    #     return self._get_min_max_date('MIN')


    
    # def update(self):

    #     max_date = self.get_max_date()
    #     ticker_list = self.get_ticker_symbols()

    #     for ticker_symbol in ticker_list:

    #         stock_frame = yf.download(ticker_symbol, start=max_date)
    #         stock_frame = stock_frame[stock_frame.index > max_date]
    #         stock_frame = stock_frame.reset_index()
    #         stock_frame.to_sql(
    #             ticker_symbol.split(".")[0], self.engine, if_exists="append"
    #         )

    #     print(f"{self.index} successfully updated")
