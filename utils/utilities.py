from sqlalchemy import create_engine, text
from yaml.loader import SafeLoader
import yaml
import os

from utils.constants import EODHD_EXCHANGE_CODES_URL, EODHD_TICKERS_URL
import requests

def get_engine(country=None):
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
    elif country == 'AU': # Connect to database
        db_connection_url = "postgresql://{}:{}@{}:{}/{}?options=-csearch_path={}".format(
            data['postgres']['username'],
            data['postgres']['password'],
            data['postgres']['host'],
            data['postgres']['port'],
            'personal_stock',
            'australia'
        )
    elif country == 'VN':
        db_connection_url = "postgresql://{}:{}@{}:{}/{}?options=-csearch_path={}".format(
            data['postgres']['username'],
            data['postgres']['password'],
            data['postgres']['host'],
            data['postgres']['port'],
            'personal_stock',
            'vietnam'
        )
    elif country == 'WORLD':
        db_connection_url = "postgresql://{}:{}@{}:{}/{}?options=-csearch_path={}".format(
            data['postgres']['username'],
            data['postgres']['password'],
            data['postgres']['host'],
            data['postgres']['port'],
            'personal_stock',
            'world'
        )
    return create_engine(db_connection_url)
    
def load_api_keys():
    with open(os.path.join('conf', 'keys.yml')) as f:
        data = yaml.load(f, Loader=SafeLoader)
    return data

def get_au_exchange_codes():
    keys = load_api_keys()
    # Get list of exchange codes
    url = EODHD_EXCHANGE_CODES_URL.format(keys['eodhd']['api_key'])
    data = requests.get(url).json()
    return [x for x in data if x['Country'] == 'Australia']


def get_au_stock_codes(exchange_code=None, source ='eodhd', engine = None, all = True):
    if source =='eodhd':
        keys = load_api_keys()
        # Get list of tickers
        url = EODHD_TICKERS_URL.format(exchange_code,keys['eodhd']['api_key'])
        if not all:
            return [ticker['Code'] for ticker in requests.get(url).json()]
        else:
            return requests.get(url).json()
    elif source == 'db':
        if engine is None:
            raise ValueError("SQLAlchemy engine must be provided to connect to DB.")
        with engine.connect() as conn:
            tickers = conn.execute(text("SELECT stock_code FROM stock_info"))
            return [ticker[0] for ticker in tickers]




def postgres_upsert(constraint_name):
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



