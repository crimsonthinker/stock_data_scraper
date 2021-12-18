import pandas as pd
from datetime import datetime
from utils.utilities import get_engine

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

    # query all data of the stock code since the first transaction date
    today = datetime.today().date()
    query = f"""
        SELECT
            date,
            close_price,
            volume
        FROM public.transaction
        WHERE
            date >= DATE '{first_transaction_date}'
            AND
            date <= DATE '{today}'
            AND
            stock_code = '{stock_code}'
        ORDER BY date
    """
    df = pd.read_sql_query(query, engine)

    moving_average_windows = [item for t in investment_preference for item in t]

    def _get_moving_average(df : pd.DataFrame, col_type : str):
        # prepare dataframe
        sma_df = df.copy(deep = True)
        ema_df = df.copy(deep = True)

        # Get the moving average with different windows
        for window in moving_average_windows:
            df[f'sma_{window}'] = df[col_type].rolling(window).mean()
            df[f'ema_{window}'] = df[col_type].ewm(span = window).mean()

        for short_ma, long_ma in investment_preference:
            # initialize MA pairs
            sma_df[f'state_{short_ma}_{long_ma}'] = 'wait'
            ema_df[f'state_{short_ma}_{long_ma}'] = 'wait'

            for i, row in df.iterrows():
                if i == 0:
                    continue

                sma_col = row.index.to_series().reset_index(drop = True)
                sma_col = sma_col[sma_col.apply(lambda x : x.startswith('sma'))]
                if not row[sma_col].isnull().values.any():
                    # short ma from below to above -> golden cross
                    if df.loc[i - 1, f'sma_{short_ma}'] < df.loc[i - 1, f'sma_{long_ma}'] and \
                        row[f'sma_{short_ma}'] > df.loc[i, f'sma_{long_ma}']:
                            sma_df.loc[i, f'state_{short_ma}_{long_ma}'] = 'bull'

                    # short ma from above to below -> death cross
                    if df.loc[i - 1, f'sma_{short_ma}'] > df.loc[i - 1, f'sma_{long_ma}'] and \
                        row[f'sma_{short_ma}'] < df.loc[i, f'sma_{long_ma}']:
                            sma_df.loc[i, f'state_{short_ma}_{long_ma}'] = 'bear'

                ema_col = row.index.to_series().reset_index(drop = True)
                ema_col = ema_col[ema_col.apply(lambda x : x.startswith('ema'))]
                if not row[ema_col].isnull().values.any():
                    # short ma from below to above -> golden cross
                    if df.loc[i - 1, f'ema_{short_ma}'] < df.loc[i - 1, f'ema_{long_ma}'] and \
                        row[f'ema_{short_ma}'] > df.loc[i, f'ema_{long_ma}']:
                        ema_df.loc[i, f'state_{short_ma}_{long_ma}'] = 'bull'

                    # short ma from above to below -> death cross
                    if df.loc[i - 1, f'ema_{short_ma}'] > df.loc[i - 1, f'ema_{long_ma}'] and \
                        row[f'ema_{short_ma}'] < df.loc[i, f'ema_{long_ma}']:
                        ema_df.loc[i, f'state_{short_ma}_{long_ma}'] = 'bear'

        return df, sma_df, ema_df

    # Get close price moving average
    p_df, p_sma_df, p_ema_df = _get_moving_average(df.copy(deep = True), 'close_price')
    # get volume moving average
    v_df, v_sma_df, v_ema_df = _get_moving_average(df.copy(deep = True), 'volume')

    return {
        'p_df' : p_df,
        'p_sma_df' : p_sma_df,
        'p_ema_df' : p_ema_df,
        'v_df' : v_df,
        'v_sma_df' : v_sma_df,
        'v_ema_df' : v_ema_df
    }

if __name__ == '__main__':
    result = moving_average_analysis('VOS', investment_preference = [(10,20),(20,50)])