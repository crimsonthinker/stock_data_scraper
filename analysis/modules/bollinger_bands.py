import pandas as pd
from utils.utilities import get_engine
from datetime import datetime
def bollinger_bands_analysis(stock_code : str, period : int = 20, multiplier : int = 2) -> pd.DataFrame:
    """Provide an analysis of stock code using Bollinger bands

    Args:
        stock_code (str): stock code
        period (int, optional): period of the window. Defaults to 20.
        multiplier (int, optional): multiplier. Defaults to 2.

    Returns:
        pd.DataFrame: data with bollinger band signals
    """

    # acquire stock data from database
    engine = get_engine()

    query = f"""
        SELECT
            first_transaction_date
        FROM
            public.stock_info
        WHERE
            stock_code = '{stock_code}'
    """
    # Get the most current transaction date
    df = pd.read_sql_query(query, engine)['first_transaction_date']
    start_date = df.max()
    end_date = datetime.today().date()

    # Query close data
    stock_query = f"""
        SELECT
            date,
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
    print("Query data")
    df = pd.read_sql_query(stock_query, engine)

    df.index = df['date']
    df = df.drop('date', axis = 1).sort_index()

    # Find upper band
    df['upper_band'] = df['close_price'].rolling(period).mean() + df['close_price'].rolling(period).std() * multiplier
    df['lower_band'] = df['close_price'].rolling(period).mean() - df['close_price'].rolling(period).std() * multiplier
    df['sma_close_price'] = df['close_price'].rolling(period).mean()

    # Remove nan value
    df = df.dropna()

    df['signal'] = 'wait'
    # Find rejection signal
    for i in range(1,len(df)):
        if df.iloc[i - 1]['sma_close_price'] > df.iloc[i - 1]['lower_band'] and \
            df.iloc[i]['sma_close_price'] < df.iloc[i]['lower_band']:
            df.iloc[i]['signal'] = 'bullish_rejection'

        if df.iloc[i - 1]['sma_close_price'] < df.iloc[i]['upper_band'] and \
            df.iloc[i]['sma_close_price'] > df.iloc[i]['upper_band']:
            df.iloc[i]['signal'] = 'bearish_rejection'

    # TODO; Find W and M pattern

    return df





