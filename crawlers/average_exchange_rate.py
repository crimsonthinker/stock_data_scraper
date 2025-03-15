import yfinance as yf
from utils.generic_utils import SQLModule
from utils.constants import  CURRENCIES

import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

class DailyAverageExchangeRate(object):
    def __init__(self):
        self._engine = SQLModule.get_engine(country='world')


    def crawl_indexes(self, period = '1d'):

        all_dfs = []
        for currency in CURRENCIES:
            module = yf.Ticker(f"USD{currency}=X")
            df = module.history(period=period)
            # convert to date
            df.index = df.index.date
            # Get the close price
            df[currency.lower()] = df['Close']
            df = df[[currency.lower()]]
            all_dfs.append(df)
            print(f'{currency}: Done.')
        df = pd.concat(all_dfs, axis=1)
        df['date'] = df.index

        # create session
        Session = sessionmaker(bind = self._engine)
        session = Session()

        # get today
        today_str = pd.Timestamp.today().strftime("%Y-%m-%d")
        # delete from today because it may update
        session.execute(text(f"DELETE from daily_average_exchange_rate_usd_based WHERE date = '{today_str}'"))
        session.commit()

        # upsert
        df.to_sql(
            name='daily_average_exchange_rate_usd_based', 
            con=self._engine.connect(), 
            schema='world', 
            if_exists='append',
            index=False, 
            method = SQLModule.db_upsert('daily_average_exchange_rate_usd_based_unique_key')
        )

if __name__ == '__main__':
    ds = DailyAverageExchangeRate()
    ds.crawl_indexes('5d')

        
            

