import yfinance as yf
import time
from utils.generic_utils import APIModule, SQLModule

from utils.constants import EXCHANGE_MAPPER, STOCK_EXCHANGE_MAPPER

class TradeInfo(object):
    def __init__(self, country):
        self._country = country
        self._engine = SQLModule.get_engine(self._country)

    def crawl_stock_prices(self, stock_codes : str = None, period='1d'):

        exchanges = APIModule.get_exchange_codes(country = self._country)
        
        # For each exchange
        for exchange_code in exchanges:
            if stock_codes is None:
                tickers = APIModule.get_stock_codes(exchange_code = exchange_code['Code'])
                tickers_with_exchange = [f'{ticker["Code"]}{EXCHANGE_MAPPER[self._country]}' for ticker in tickers]
            else:
                tickers = stock_codes
                tickers_with_exchange = [f'{ticker}{EXCHANGE_MAPPER[self._country]}' for ticker in tickers]
            for ticker_code, ticker in zip(tickers_with_exchange,tickers):
                max_attempts = 5 
                attempt = 1
                while attempt <= max_attempts:
                    try:
                        module = yf.Ticker(ticker_code)
                        sub_df = module.history(period=period).reset_index()
                        break
                    except:
                        attempt += 1
                        time.sleep(20)
                    # module = yf.Ticker(ticker_code)
                    # sub_df = module.history(period=period).reset_index()
                try:
                    sub_df['Date'] = sub_df['Date'].dt.date
                    # Add some columns
                    sub_df['stock_exchange'] = STOCK_EXCHANGE_MAPPER[self._country]
                    sub_df['stock_code'] = ticker['Code']
                    # Rename columns
                    sub_df = sub_df.rename(columns = {
                        'Date' : 'date',
                        'Open' : 'open', 
                        'High' : 'high', 
                        'Low' : 'low', 
                        'Close' : 'close', 
                        'Volume' : 'volume'
                    })
                    # filter columns
                    # Remove row with nan values
                    sub_df = sub_df[['stock_exchange','stock_code','date','open','high','low','close','volume']].dropna()
                    if len(sub_df) > 0:
                        print(f'[{self._country}] {ticker_code}: Done.')
                        sub_df.to_sql(
                            name='transaction', 
                            con=self._engine.connect(), 
                            schema=self._country, 
                            if_exists='append',
                            index=False, 
                            method = SQLModule.db_upsert('transaction_unique_key')
                        )
                    else:
                        print(f'[{self._country}] {ticker_code}\'s data: Not available')
                except:
                    pass


if __name__ == '__main__':
    for country in ['australia', 'vietnam', 'united_states']:
        ds = TradeInfo(country = country)
        ds.crawl_stock_prices(period = '5d')
    # ds = DailyTransaction(country = 'australia')
    # ds.crawl_stock_prices(stock_codes = ['NXL'], period = 'all')

        
            

