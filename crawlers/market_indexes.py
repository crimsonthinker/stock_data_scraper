import yfinance as yf
from utils.generic_utils import SQLModule
from utils.constants import MARKET_INDICES, INDEXES_BY_COUNTRY


class IndexInfo(object):
    def __init__(self):
        self._engine = SQLModule.get_engine(country='world')


    def crawl_indexes(self, period = '1d'):
        module = yf.Tickers(list(MARKET_INDICES.keys()))
        df = module.history(period=period)

        for market_index in MARKET_INDICES:
            the_country = None
            for country in INDEXES_BY_COUNTRY:
                if MARKET_INDICES[market_index] in INDEXES_BY_COUNTRY[country]:
                    the_country = country
                    break
            # Extract data from ticker
            try:
                sub_df = df.loc[:,(slice(None),market_index)].reset_index()
                sub_df.columns = sub_df.columns.map(lambda x : x[0].lower())
                sub_df = sub_df.rename(columns = {'stock splits':'stock_splits'})
                sub_df = sub_df.dropna()
                sub_df['country'] = the_country
            except:
                print(f"{MARKET_INDICES[market_index]}: Delisted.")
                continue
            # reformat the date
            sub_df['date'] = sub_df['date'].dt.date
            # Add some columns
            sub_df['stock_index'] = MARKET_INDICES[market_index]
            sub_df.to_sql(
                name='stock_indexes', 
                con=self._engine.connect(), 
                schema='world', 
                if_exists='append',index=False, 
                method = SQLModule.db_upsert('stock_index_unique_key')
            )
            print(f'{MARKET_INDICES[market_index]}: Done.')

if __name__ == '__main__':
    ds = IndexInfo()
    ds.crawl_indexes('max')

        
            

