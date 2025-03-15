import yfinance as yf
from utils.generic_utils import SQLModule, APIModule
import pandas as pd
from datetime import date
import sqlalchemy
import time

from utils.constants import COUNTRY_MAPPER, EXCHANGE_MAPPER

class StockCodes(object):
    def __init__(self, country):
        self._country = country
        self._engine = SQLModule.get_engine(country=self._country)

    def crawl(self):
        exchanges = APIModule.get_exchange_codes(country = self._country)

        # For each exchange
        for exchange_code in exchanges:
            tickers = APIModule.get_stock_codes(exchange_code = exchange_code['Code'])
            data = []
            max_attempts = 5
            for ticker in tickers:  
                attempt = 1
                while attempt <= max_attempts:
                    try:
                        print(f'[{self._country}] Extracting information for ticker {ticker["Code"]}{EXCHANGE_MAPPER[self._country]}')
                        company_name = ticker['Name'].replace('\'','"')
                        stock_code = ticker['Code']
                        stock_exchange = exchange_code['Code']
                        last_updated_date = date.today().strftime("%Y-%m-%d")
                        # Extract fundamental data
                        module = yf.Ticker(f'{ticker["Code"]}{EXCHANGE_MAPPER[self._country]}')
                        data.append({
                            'company_name' : company_name,
                            'stock_code' : stock_code,
                            'stock_exchange': stock_exchange,
                            'last_updated_date': last_updated_date,
                            'fundamental' : module.info
                        })
                        break
                    except Exception as e:
                        attempt += 1
                        if attempt > max_attempts:
                            print(f'[{self._country}] Ticker code {ticker["Code"]} failed')
                            print(f'[{self._country}]', e)
                        time.sleep(20)
            df = pd.DataFrame(data)
            try:
                df.to_sql(
                    name = 'stock_info', 
                    con=self._engine.connect(), 
                    schema = self._country, 
                    if_exists='append',
                    index=False, 
                    dtype = {'fundamental' : sqlalchemy.types.JSON}, method = SQLModule.db_upsert('stock_info_pkey'))
            except Exception as e:
                print(f"[{self._country}] Problem updating stock codes for {self._country}")
                print(e)
                        

if __name__ == '__main__':
    for country in ['vietnam', 'australia', 'united_states']:
        hs = StockCodes(country = country)
        hs.crawl()