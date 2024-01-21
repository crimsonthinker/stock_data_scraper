import yfinance as yf
from utils.utilities import get_engine, get_au_exchange_codes, get_au_stock_codes, postgres_upsert
import pandas as pd
from datetime import date
import sqlalchemy

class StockCodes(object):
    def __init__(self, country='AU'):
        self._country = country
        self._engine = get_engine(country=self._country)

    def crawl(self):
        au_exchanges = get_au_exchange_codes()

        for exchange_code in au_exchanges:
            tickers = get_au_stock_codes(exchange_code['Code'], all = True)
            data = []
            for ticker in tickers:
                print(f'Extracting information for ticker {ticker["Code"]}')
                company_name = ticker['Name'].replace('\'','"')
                stock_code = ticker['Code']
                stock_exchange = exchange_code['Code']
                last_updated_date = date.today().strftime("%Y-%m-%d")
                # Extract fundamental data
                module = yf.Ticker(f'{ticker["Code"]}.AX')
                data.append({
                    'company_name' : company_name,
                    'stock_code' : stock_code,
                    'stock_exchange': stock_exchange,
                    'last_updated_date': last_updated_date,
                    'fundamental' : module.info
                })
            df = pd.DataFrame(data)
            df.to_sql(name = 'stock_info', con=self._engine.connect(), schema='australia', if_exists='append',index=False, dtype = {'fundamental' : sqlalchemy.types.JSON}, method = postgres_upsert('stock_info_pkey'))


if __name__ == '__main__':
    hs = StockCodes()
    hs.crawl()