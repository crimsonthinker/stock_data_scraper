from numpy import sign
import pandas as pd
from datetime import datetime
from utils.utilities import get_engine
from itertools import combinations
import math

def moving_average_analysis(stock_code : str, investment_preference : list) -> pd.DataFrame:
    """Analyze stock data using Moving Average Analysis

    Args:
        stock_code (str): stock code 
        investment_preference (list) : pairs of windows. Example: [
            (10, 20)
            (20, 50)
            (50, 100)
            (100, 200)
            (200, 500)
        ]
        It can be any pair of moving average window.
        The first element of the pair must be shorter than the second one.

    Returns:
        pd.DataFrame
    """    

    engine = get_engine()
    # Get start date of stock code
    stock_query = f"""
        SELECT 
            first_transaction_date
        FROM public.stock_info
        WHERE
            stock_code = '{stock_code}'
    """
    first_transaction_date = pd.read_sql_query(stock_query, engine).iloc[0]['first_transaction_date']

    result = pd.DataFrame(columns = ['stock_code', 'buy_today', 'profit'])

    # query all data of the stock code since the first transaction date
    today = datetime.today().date()
    query = f"""
        SELECT * 
        FROM public.transaction
        WHERE
            date >= DATE '{first_transaction_date}'
            AND
            date <= DATE '{today}'
            AND
            stock_code = '{stock_code}'
    """
    df = pd.read_sql_query(query, engine)

    moving_average_windows = [item for t in investment_preference for item in t]
    # Get the moving average with different windows
    for window in moving_average_windows:
        df[f'sma_{window}'] = df['close_price'].rolling(window).mean()
        df[f'ema_{window}'] = df['close_price'].ewm(span = window).mean()

    for short_ma, long_ma in investment_preference:
        # initialize MA pairs
        df[f'state_sma_{short_ma}_{long_ma}'] = 'wait'
        df[f'state_ema_{short_ma}_{long_ma}'] = 'wait'
        
        for i in df.index[1:]: # start from the second row
            # no rows should be NAN
            if not(math.isnan(df.loc[i, f'sma_{short_ma}']) or \
                math.isnan(df.loc[i, f'sma_{long_ma}']) or \
                    math.isnan(df.loc[i - 1, f'sma_{short_ma}']) or \
                        math.isnan(df.loc[i - 1, f'sma_{long_ma}'])):
                        # short ma from below to above -> golden cross
                        if df.loc[i, f'sma_{short_ma}'] > df.loc[i, f'sma_{long_ma}'] and df.loc[i - 1, f'sma_{short_ma}'] < df.loc[i - 1, f'sma_{long_ma}']:
                            df.loc[i, f'state_sma_{short_ma}_{long_ma}'] = 'bear'

                        # short ma from above to below -> death cross
                        if df.loc[i, f'sma_{short_ma}'] < df.loc[i, f'sma_{long_ma}'] and df.loc[i - 1, f'sma_{short_ma}'] > df.loc[i - 1, f'sma_{long_ma}']:
                            df.loc[i, f'state_sma_{short_ma}_{long_ma}'] = 'bull'

            # no rows should be NAN
            if not(math.isnan(df.loc[i, f'ema_{short_ma}']) or \
                math.isnan(df.loc[i, f'ema_{long_ma}']) or \
                    math.isnan(df.loc[i - 1, f'ema_{short_ma}']) or \
                        math.isnan(df.loc[i - 1, f'ema_{long_ma}'])):
                        # short ma from below to above -> golden cross
                        if df.loc[i, f'ema_{short_ma}'] > df.loc[i, f'ema_{long_ma}'] and df.loc[i - 1, f'ema_{short_ma}'] < df.loc[i - 1, f'ema_{long_ma}']:
                            df.loc[i, f'state_ema_{short_ma}_{long_ma}'] = 'bear'

                        # short ma from above to below -> death cross
                        if df.loc[i, f'ema_{short_ma}'] < df.loc[i, f'ema_{long_ma}'] and df.loc[i - 1, f'ema_{short_ma}'] > df.loc[i - 1, f'ema_{long_ma}']:
                            df.loc[i, f'state_ema_{short_ma}_{long_ma}'] = 'bull'

    return df