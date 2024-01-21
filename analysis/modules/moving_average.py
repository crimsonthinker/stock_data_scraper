import pandas as pd
from functools import reduce
from utils.utilities import get_engine

def moving_average_analysis(
        stock_codes : str,
        window : list = (50,100), 
        country = 'AU',
        lookback_window : int = 14,
    ) -> pd.DataFrame:
    """Analyze stock data using Moving Average Analysis

    Args:
        stock_code (str): stock code 
        investment_preference (list) : pairs of windows. Example:
            (10, 20)
            (20, 50)
            (50, 100)
            (100, 200)
            (200, 500)
        It can be any pair of moving average window.
        The first element of the pair must be shorter than the second one.

    Returns:
        pd.DataFrame
    """    

    engine = get_engine(country = country)

    def _get_moving_average(df : pd.DataFrame, col_type : str):

        # Get the moving average with different windows
        short_ma, long_ma = window
        for w in window:
            # sma: Single moving average
            df[f'sma_{w}'] = df[col_type].rolling(w).mean()
            # ema: exponential moving average
            df[f'ema_{w}'] = df[col_type].ewm(span = w).mean()

        
        # initialize MA pairs
        df[f'sma_trend'] = 'wait'
        df[f'ema_trend'] = 'wait'

        # import pdb; pdb.set_trace()
        for i, (_,row) in enumerate(df.iterrows()):
            if i == 0:
                continue

            sma_col = row.index.to_series().reset_index(drop = True)
            sma_col = sma_col[sma_col.apply(lambda x : x.startswith('sma'))]
            if not row[sma_col].isnull().values.any():
                # short ma from below to above -> golden cross
                if df.iloc[i - 1][f'sma_{short_ma}'] < df.iloc[i - 1][f'sma_{long_ma}'] and \
                    row[f'sma_{short_ma}'] > df.iloc[i][f'sma_{long_ma}']:
                        df.iloc[i][f'sma_trend'] = 'bull'

                # short ma from above to below -> death cross
                if df.iloc[i - 1][f'sma_{short_ma}'] > df.iloc[i - 1][f'sma_{long_ma}'] and \
                    row[f'sma_{short_ma}'] < df.iloc[i][f'sma_{long_ma}']:
                        df.iloc[i][f'sma_trend'] = 'bear'

            ema_col = row.index.to_series().reset_index(drop = True)
            ema_col = ema_col[ema_col.apply(lambda x : x.startswith('ema'))]
            if not row[ema_col].isnull().values.any():
                # short ma from below to above -> golden cross
                if df.iloc[i - 1][f'ema_{short_ma}'] < df.iloc[i - 1][f'ema_{long_ma}'] and \
                    row[f'ema_{short_ma}'] > df.iloc[i][f'ema_{long_ma}']:
                    df.iloc[i][f'ema_trend'] = 'bull'

                # short ma from above to below -> death cross
                if df.iloc[i - 1][f'ema_{short_ma}'] > df.iloc[i - 1][f'ema_{long_ma}'] and \
                    row[f'ema_{short_ma}'] < df.iloc[i][f'ema_{long_ma}']:
                    df.iloc[i][f'ema_trend'] = 'bear'

        return df

    # query all data of the stock code
    dfs = []
    for stock_code in stock_codes:
        query = f"""
            SELECT
                date,
                close
            FROM transaction
            WHERE
                stock_code = '{stock_code}'
            ORDER BY date
        """
        print(f"Query {stock_code}")
        df = pd.read_sql_query(query, engine)

        df.index = df['date']
        df = df.drop('date', axis = 1)

        # Remove nan value
        df = df.dropna() # IMPORTANT??

        # Get close price moving average
        # NOTE: This approach can be used for volume as well
        df = _get_moving_average(df.copy(deep = True), 'close')

        df = df[['close',f'sma_{window[0]}',f'sma_{window[1]}', 'sma_trend', f'ema_{window[0]}', f'ema_{window[1]}', 'ema_trend']]

        # Change column to multi-index
        df.columns = pd.MultiIndex.from_tuples([(stock_code,col) for col in df.columns])
        # dfs.append(df[-lookback_window:].reset_index())
        dfs.append(df.iloc[-lookback_window:].reset_index())

    return reduce(lambda l,r: pd.merge(l,r, on='date', how='outer'), dfs).sort_values(by='date').reset_index(drop = True)
