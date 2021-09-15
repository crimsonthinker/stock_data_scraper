import pandas as pd
from datetime import datetime, timedelta
import talib

from utils.utilities import get_engine

def rsi(stock_code : str, day_interval : int = 14) -> pd.DataFrame:
    """calculate relative strength index for the stock code

    Args:
        stock_code (str): stock code
        day_interval (int) : period to get RSI. Must be larger than 1.
    """
    engine = get_engine()

    # Get 1 year data
    end_date = datetime.today().date()
    start_date = end_date - timedelta(days = day_interval)

    stock_query = f"""
        SELECT
            close_price
        FROM public.transaction
        WHERE
            stock_code = '{stock_code}'
            AND
            date >= DATE '{start_date}'
            AND
            date <= DATE '{end_date}'
    """
    print("Query data")
    df = pd.read_sql_query(stock_query, engine)

    rsi_value = talib.RSI(df['close_price'])

    return {
        'rsi_value' : rsi_value,
        'action' : 'ready_to_bear' if rsi_value > 70 else ('ready_to_bull' if rsi < 30 else 'wait')
    }
    