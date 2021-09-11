from numpy import sign
import pandas as pd
from datetime import datetime
from utils.utilities import get_engine
from itertools import combinations
import math

def moving_average_analysis(stock_code : str, investment_preference : dict) -> pd.DataFrame:
    """Analyze stock data using Moving Average Analysis

    Args:
        stock_code (str): stock code 
        investment_prefrence (dict) : your way of investing. Example: {
            (10, 20) : 0.4,
            (20, 50) : 0.2,
            (50, 100) : 0.2,
            (100, 200) : 0.1,
            (200, 500) : 0.1
        }
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
        df[f'ma_{window}'] = df['close_price'].rolling(window).mean()

    for short_ma, long_ma in investment_preference:
        # initialize MA pairs
        df[f'state_{short_ma}_{long_ma}'] = 'wait'
        
        for i in df.index[1:]: # start from the second row
            # no rows should be NAN
            if math.isnan(df.loc[i, f'ma_{short_ma}']) or \
                math.isnan(df.loc[i, f'ma_{long_ma}']) or \
                    math.isnan(df.loc[i - 1, f'ma_{short_ma}']) or \
                        math.isnan(df.loc[i - 1, f'ma_{long_ma}']):
                        continue 


            # short ma from below to above -> golden cross
            if df.loc[i, f'ma_{short_ma}'] > df.loc[i, f'ma_{long_ma}'] and df.loc[i - 1, f'ma_{short_ma}'] < df.loc[i - 1, f'ma_{long_ma}']:
                df.loc[i, f'state_{short_ma}_{long_ma}'] = 'bear'

            # short ma from above to below -> death cross
            if df.loc[i, f'ma_{short_ma}'] < df.loc[i, f'ma_{long_ma}'] and df.loc[i - 1, f'ma_{short_ma}'] > df.loc[i - 1, f'ma_{long_ma}']:
                df.loc[i, f'state_{short_ma}_{long_ma}'] = 'bull'

    recent_state = df.iloc[-1]

    # personal algorithm: using weighted average to calculate final action
    # numerator = 0
    # denominator = 0
    # for key in investment_preference:
    #     short_ma, long_ma = key
    #     denominator += investment_preference[key]
    #     numerator += (1 if recent_state[f'state_{short_ma}_{long_ma}'] == 'bear' else \
    #         0.5 if recent_state[f'state_{short_ma}_{long_ma}'] == 'wait' else 0.0) * investment_preference[key]

    # final_action = numerator / denominator
    # action_score = final_action
    # if final_action >= 0.45 and final_action <= 0.55: # safe spot for waiting
    #     final_action = 'wait'
    # elif final_action > 0.6:
    #     final_action = 'bear'
    # else:
    #     final_action = 'bull'

    # recent_state.loc['final_action'] = final_action
    # recent_state.loc['action_score'] = action_score

    return df