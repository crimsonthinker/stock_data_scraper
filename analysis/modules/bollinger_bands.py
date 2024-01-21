import pandas as pd
from utils.utilities import get_engine
from datetime import datetime
from typing import List
from dateutil.relativedelta import relativedelta
from functools import reduce

def bollinger_bands_analysis(
        stock_codes : List[str], 
        country = 'AU', 
        days = 365,
        period : int = 20, 
        k : int = 2, 
        lookback_window : int = 14
    ) -> pd.DataFrame:
    """Provide an analysis of stock code using Bollinger bands

    Args:
        stock_code (str): stock code
        period (int, optional): period of the window. Defaults to 20.
        days (int, optional): Time range. Defaults to 365 days.
        multiplier (int, optional): multiplier. Defaults to 2.

    Returns:
        pd.DataFrame: data with bollinger band signals
    """

    # acquire stock data from database
    engine = get_engine(country = country)

    # Get time range
    end_date = datetime.today().date()
    start_date = end_date - relativedelta(days = days)

    # Query close data
    dfs = []
    for stock_code in stock_codes:
        stock_query = f"""
            SELECT
                date,
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

        df.index = df['date']
        df = df.drop('date', axis = 1)

        # Remove nan value
        df = df.dropna()

        # Find upper band
        df['upper_band'] = df['close'].rolling(period).mean() + df['close'].rolling(period).std() * k
        df['lower_band'] = df['close'].rolling(period).mean() - df['close'].rolling(period).std() * k
        df['sma_close'] = df['close'].rolling(period).mean()
        df['w_pattern'] = (df['close'].shift(1) > df['lower_band'].shift(1)) & (df['close'] < df['lower_band'])
        df['m_pattern'] = (df['close'].shift(1) < df['upper_band'].shift(1)) & (df['close'] > df['upper_band'])

        # Find rejection signal
        df['bollinger_trend'] = 'wait'
        for i in range(1,len(df)):
            if df.iloc[i - 1]['sma_close'] > df.iloc[i - 1]['lower_band'] and \
                df.iloc[i]['sma_close'] < df.iloc[i]['lower_band']:
                df.iloc[i]['bollinger_trend'] = 'bull'

            if df.iloc[i - 1]['sma_close'] < df.iloc[i]['upper_band'] and \
                df.iloc[i]['sma_close'] > df.iloc[i]['upper_band']:
                df.iloc[i]['bollinger_trend'] = 'bear'

        df['wm_trend'] = df.apply(lambda row : 'wait' if row['w_pattern'] == row['m_pattern'] else ('bull' if row['w_pattern'] else 'bear'), axis = 1)

        df = df[['close','bollinger_trend','wm_trend']]

        # Change column to multi-index
        df.columns = pd.MultiIndex.from_tuples([(stock_code,col) for col in df.columns])
        # dfs.append(df[-lookback_window:].reset_index())
        dfs.append(df.iloc[-lookback_window:].reset_index())

    return reduce(lambda l,r: pd.merge(l,r, on='date', how='outer'), dfs).sort_values(by='date').reset_index(drop = True)





