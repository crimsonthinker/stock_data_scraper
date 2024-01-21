import pandas as pd
from datetime import datetime, timedelta
import talib
from typing import List
from functools import reduce

from utils.utilities import get_engine

def momentum_indicators(
        stock_codes : List[str], 
        country = 'AU',
        days : int = 90, 
        period = 14,
        rsi_range = [30,70],
        adx_threshold = 25,
        lookback_window : int = 7
    ) -> pd.DataFrame:
    """calculate df relating to momentum
    Including:
    RSI

    Args:
        stock_code (str): stock code
        day_interval (int) : period to get RSI. Must be larger than 1.
        lookback_window (int) : period of day to return DataFrame
    """
    engine = get_engine(country = country)

    # Get 1 year data
    end_date = datetime.today().date()
    start_date = end_date - timedelta(days = days)

    dfs = []
    for stock_code in stock_codes:
        stock_query = f"""
            SELECT
                date,
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
        df = pd.read_sql_query(stock_query, engine)

        # Remove nan value
        df.index = df['date']
        df = df.drop('date', axis = 1)

        df = df.dropna() # IMPORTANT??

        # Relative strength index
        df['rsi'] = talib.RSI(df['close'], timeperiod = period).to_numpy()
        df['rsi_trend'] = df['rsi'].apply(lambda rsi_value: 'bear' if rsi_value > rsi_range[1] else ('bull' if rsi_value < rsi_range[0] else 'wait'))

        # Average Directional Index
        # FIXME: Parameters for hard-coded values
        df['adx'] = talib.ADX(df['high'], df['low'], df['close'], timeperiod = period).to_numpy()
        df['minus_di'] = talib.MINUS_DI(df['high'], df['low'], df['close'], timeperiod = period).to_numpy()
        df['plus_di'] = talib.PLUS_DI(df['high'], df['low'], df['close'], timeperiod = period).to_numpy()
        df['adx_trend'] = 'wait'
        for i in range(1,len(df)):
            if df.iloc[i - 1]['adx'] < adx_threshold and df.iloc[i]['adx'] > adx_threshold and df.iloc[i]['plus_di'] > df.iloc[i]['minus_di']:
                df['adx_trend'].iloc[i] = 'bull'
            elif df.iloc[i - 1]['adx'] < adx_threshold and df.iloc[i]['adx'] > adx_threshold and df.iloc[i]['plus_di'] < df.iloc[i]['minus_di']:
                df['adx_trend'].iloc[i] = 'bear'

        df = df[['close','rsi','rsi_trend','adx','adx_trend']]

        # Set lookback windows
        df = df.iloc[-lookback_window:]

        # Change column to multi-index
        df.columns = pd.MultiIndex.from_tuples([(stock_code,col) for col in df.columns])

        dfs.append(df.reset_index())
    
    return reduce(lambda l,r: pd.merge(l,r, on='date', how='outer'), dfs).sort_values(by='date').reset_index(drop = True)

def volatility_df(stock_code : str):
    pass
    
if __name__ == '__main__':
    momentum_indicators('SYI')