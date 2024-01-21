import yfinance as yf
from utils.utilities import get_engine, get_au_exchange_codes, get_au_stock_codes, postgres_upsert

class DailyTransaction(object):
    def __init__(self, country):
        self._country = country
        self._engine = get_engine(country='AU')

    def crawl_stock_prices(self, period='1d'):
        if self._country == 'AU':
            tickers = get_au_stock_codes(source ='db', engine = self._engine)
        else:
            pass
        tickers_with_exchange = [f'{ticker}.AX' for ticker in tickers]
        module = yf.Tickers(tickers_with_exchange)
        df = module.history(period=period)

        for ticker_code in tickers:
            # Extract data from ticker
            try:
                sub_df = df.loc[:,(slice(None),f'{ticker_code}.AX')].reset_index()
                sub_df.columns = sub_df.columns.map(lambda x : x[0])
            except:
                print(f"{ticker_code}: Delisted.")
                continue
            # reformat the date
            sub_df['Date'] = sub_df['Date'].dt.date
            # Add some columns
            sub_df['stock_exchange'] = 'AU' # FIXME: For now
            sub_df['stock_code'] = ticker_code
            sub_df['adjusted_close'] = None # FIXME: Add this in the future
            # Rename columns
            sub_df = sub_df.rename(columns = {'Date' : 'date','Open' : 'open', 'High' : 'high', 'Low' : 'low', 'Close' : 'close', 'Volume' : 'volume'})
            # filter columns
            sub_df = sub_df[['stock_exchange','stock_code','date','open','high','low','close','adjusted_close','volume']]
            print(f'{ticker_code}: Done.')
            sub_df.to_sql(name='transaction', con=self._engine.connect(), schema='australia', if_exists='append',index=False, method = postgres_upsert('transaction_unique_key'))

if __name__ == '__main__':
    ds = DailyTransaction(country='AU')
    ds.crawl_stock_prices('1w')

        
            

