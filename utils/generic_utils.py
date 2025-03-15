from sqlalchemy import create_engine, text
from yaml.loader import SafeLoader
import yaml
import os
import pandas as pd

from utils.constants import EODHD_EXCHANGE_CODES_URL, EODHD_TICKERS_URL, COUNTRY_MAPPER
import requests

class SQLModule:

    @staticmethod
    def get_engine(country = None):
        # Load db_config.yaml
        with open(os.path.join('conf', 'db_config.yml')) as f:
            data = yaml.load(f, Loader=SafeLoader)
        if country is None:
            db_connection_url = "postgresql://{}:{}@{}:{}".format(
                data['postgres']['username'],
                data['postgres']['password'],
                data['postgres']['host'],
                data['postgres']['port']
            )
        else: # Connect to specific scope
            db_connection_url = "postgresql://{}:{}@{}:{}/{}?options=-csearch_path={}".format(
                data['postgres']['username'],
                data['postgres']['password'],
                data['postgres']['host'],
                data['postgres']['port'],
                'personal_stock',
                country
            )
        return create_engine(db_connection_url, pool_size=20, max_overflow = 5)
    
    @staticmethod
    def db_upsert(constraint_name):
        def _postgres_upsert(table, conn, keys, data_iter):
            from sqlalchemy.dialects.postgresql import insert

            data = [dict(zip(keys, row)) for row in data_iter]

            insert_statement = insert(table.table).values(data)
            upsert_statement = insert_statement.on_conflict_do_update(
                constraint = constraint_name,
                set_={c.key: c for c in insert_statement.excluded},
            )
            conn.execute(upsert_statement)
        return _postgres_upsert
    
class APIModule:

    @staticmethod
    def _load_api_keys():
        with open(os.path.join('conf', 'keys.yml')) as f:
            data = yaml.load(f, Loader=SafeLoader)
        return data
    
    @staticmethod
    def get_exchange_codes(country : str = None):
        keys = APIModule._load_api_keys()
        # Get list of exchange codes
        url = EODHD_EXCHANGE_CODES_URL.format(keys['eodhd']['api_key'])
        data = requests.get(url).json()
        if country is None:
            return data
        else:
            return [x for x in data if x['Country'] in COUNTRY_MAPPER[country]]
        
    @staticmethod
    def get_stock_codes(exchange_code = None, engine = None):
        if exchange_code is not None and engine is not None:
            raise ValueError("[exchange_code] and [engine] should not be both None")
        

        if exchange_code is not None:
            keys = APIModule._load_api_keys()
            # Get list of tickers
            url = EODHD_TICKERS_URL.format(exchange_code,keys['eodhd']['api_key'])
            return requests.get(url).json()
        else:
            if engine is None:
                raise ValueError("SQLAlchemy engine must be provided to connect to DB.")
            with engine.connect() as conn:
                tickers = conn.execute(text("SELECT stock_code FROM stock_info"))
                return [ticker[0] for ticker in tickers]




