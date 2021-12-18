import pandas as pd
from datetime import datetime, timedelta
import talib

from utils.utilities import get_engine

def momentum_indicators(stock_code : str, day_interval : int = 252, lookback_window : int = 7) -> pd.DataFrame:
    """calculate indicators relating to momentum
    Including:
    RSI

    Args:
        stock_code (str): stock code
        day_interval (int) : period to get RSI. Must be larger than 1.
        lookback_window (int) : period of day to return DataFrame
    """
    engine = get_engine()

    # Get 1 year data
    end_date = datetime.today().date()
    start_date = end_date - timedelta(days = day_interval)

    stock_query = f"""
        SELECT
            date,
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
    print("Query data")
    df = pd.read_sql_query(stock_query, engine)

    # initializing dataframe
    indicators = pd.DataFrame(index = df['date'])

    # Relative strength index
    indicators['RSI'] = talib.RSI(df['close_price']).to_numpy()
    indicators['RSI_trend'] = indicators['RSI'].apply(lambda rsi_value: 'bearish_trend' if rsi_value > 70 else ('bullish_trend' if rsi_value < 30 else 'wait'))

    # Average Directional Index
    indicators['ADX'] = talib.ADX(df['highest_price'], df['lowest_price'], df['close_price'], timeperiod = 14).to_numpy()
    indicators['MINUS_DI'] = talib.MINUS_DI(df['highest_price'], df['lowest_price'], df['close_price'], timeperiod = 14).to_numpy()
    indicators['PLUS_DI'] = talib.PLUS_DI(df['highest_price'], df['lowest_price'], df['close_price'], timeperiod = 14).to_numpy()
    indicators['ADX_trend'] = 'wait'
    for i in range(1,len(indicators)):
        if indicators.iloc[i - 1]['ADX'] < 25 and indicators.iloc[i]['ADX'] > 25 and indicators.iloc[i]['PLUS_DI'] > indicators.iloc[i]['MINUS_DI']:
            indicators['ADX_trend'].iloc[i] = 'bullish_trend'
        elif indicators.iloc[i - 1]['ADX'] < 25 and indicators.iloc[i]['ADX'] > 25 and indicators.iloc[i]['PLUS_DI'] < indicators.iloc[i]['MINUS_DI']:
            indicators['ADX_trend'].iloc[i] = 'bearish_trend'

    
    return indicators.iloc[:-7]

def volatility_indicators(stock_code : str):
    pass
    
if __name__ == '__main__':
    momentum_indicators('ACB')