import pandas as pd
import talib
from utils.utilities import get_engine
from datetime import datetime
from typing import List
from functools import reduce
from dateutil.relativedelta import relativedelta

from utils.constants import CANDLE_RANKINGS

def candlestick_patterns(
        stock_codes: List[str], 
        country = 'AU',
        days : int = 120, 
        lookback_window : int = 14, 
    ) -> pd.DataFrame:
    """Input is a Pandas Dataframe that has
    open_price
    close_price
    highest_price
    lowest_price
    And it can be either data from stocks or index

    Args:
        stock_code (pd.DataFrame): stock code
        day_interval (int): day interval
        lookback_window (int) : lookback window of the result
    """

    engine = get_engine(country = country)
    # we only need 2 to 3 days to analyze candlestick
    end_date = datetime.today().date()
    start_date = end_date - relativedelta(days = days)

    dfs = []
    for stock_code in stock_codes:
        query = f"""
            SELECT
                date,
                open,
                high,
                low,
                close
            FROM transaction
            WHERE 
                stock_code = '{stock_code}'
                AND
                date >= DATE '{start_date}'
                AND
                date <= DATE '{end_date}'
            ORDER BY date
        """
        print(f"Query {stock_code}")

        stock_data = pd.read_sql_query(query, engine)
        # Remove nan value
        stock_data = stock_data.dropna() # IMPORTANT??

        stock_data.index = stock_data['date']
        stock_data = stock_data.drop('date', axis = 1)

        # Get list of candle name from CANDLE_RANKINGS
        candle_names = []
        for candle in CANDLE_RANKINGS:
            name,_ = candle.split("_")
            candle_names.append(name)
        candle_names = list(set(candle_names))

        # find patterns for data
        for candle in candle_names:
            stock_data[candle] = getattr(talib, candle)(stock_data['open'], stock_data['high'], stock_data['low'], stock_data['close'])

        worst_rank = max(list(CANDLE_RANKINGS.values()))

        def make_decision(row):
            proposed_candles = {}
            for candle in candle_names:
                if row[candle] != 0:
                    proposed_candles[candle] = row[candle]
            if len(proposed_candles) == 0:
                row['trend'] = 'wait'
                row['score'] = 0
            else:
                score = 0
                for candle in proposed_candles:
                    action = f'{candle}_Bull' if proposed_candles[candle] > 0 else f'{candle}_Bear'
                    score += proposed_candles[candle] * (worst_rank - CANDLE_RANKINGS[action])
                if score > 0:
                    row['trend'] = 'bull'
                elif score == 0:
                    row['trend'] = 'wait'
                else:
                    row['trend'] = 'bear'
                row['score'] = score
            return row

        stock_data = stock_data.apply(make_decision, axis = 1)

        # dropcolumns
        stock_data = stock_data[['close','score','trend']]
        stock_data = stock_data.iloc[-lookback_window:]

        # Change column to multi-index
        stock_data.columns = pd.MultiIndex.from_tuples([(stock_code,col) for col in stock_data.columns])

        dfs.append(stock_data.reset_index())
    return reduce(lambda l,r: pd.merge(l,r, on='date', how='outer'), dfs).sort_values(by='date').reset_index(drop = True)







