import pandas as pd
import talib
from utils.utilities import get_engine
from datetime import datetime
from dateutil.relativedelta import relativedelta

from utils.constants import CANDLE_RANKINGS

def candlestick_patterns(stock_code: str) -> pd.DataFrame:
    """Input is a Pandas Dataframe that has
    open_price
    close_price
    highest_price
    lowest_price
    And it can be either data from stocks or index

    Args:
        stock_code (pd.DataFrame): stock code
    """

    engine = get_engine()
    # we only need 2 to 3 days to analyze candlestick
    end_date = datetime.today().date()
    start_date = end_date - relativedelta(days = 10)

    query = f"""
        SELECT
            stock_code,
            date,
            open_price,
            highest_price,
            lowest_price,
            close_price
        FROM public.transaction
        WHERE 
            stock_code = '{stock_code}'
            AND
            date >= DATE '{start_date}'
            AND
            date <= DATE '{end_date}'
        ORDER BY date
    """
    stock_data = pd.read_sql_query(query, engine)
    stock_data = stock_data.rename(columns = {
        'open_price' : 'open',
        'close_price' : 'close',
        'highest_price' : 'high',
        'lowest_price' : 'low'
    })

    # Get list of candle name from CANDLE_RANKINGS
    candle_names = []
    for candle in CANDLE_RANKINGS:
        name,_ = candle.split("_")
        candle_names.append(name)
    candle_names = list(set(candle_names))

    # find patterns for data
    for candle in candle_names:
        stock_data[candle] = getattr(talib, candle)(stock_data['open'], stock_data['high'], stock_data['low'], stock_data['close'])

    def make_decision(row):
        proposed_candles = {}
        for candle in candle_names:
            if row[candle] != 0:
                proposed_candles[candle] = row[candle]
        if len(proposed_candles) == 0:
            row['action'] = 'wait'
        else:
            score = 0
            for candle in proposed_candles:
                action = f'{candle}_Bull' if proposed_candles[candle] > 0 else f'{candle}_Bear'
                score += proposed_candles[candle] * CANDLE_RANKINGS[action]
            if score > 0:
                row['action'] = 'bull'
            elif score == 0:
                row['action'] = 'wait'
            else:
                row['action'] = 'bear'
        return row
    stock_data = stock_data.apply(make_decision, axis = 1)

    # rename again
    stock_data = stock_data.rename(columns = {
        'open' : 'open_price',
        'close' : 'close_price',
        'high' : 'highest_price',
        'low' : 'lowest_price'
    })

    return stock_data.iloc[-1]







