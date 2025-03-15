import pandas as pd
import holidays

class StockPriceProcess:
    def frame_var(
            df : pd.DataFrame, 
            target_col : str = 'stock_code', 
            price_col : str = 'close', 
            date_list : list = None
        ):
        # Create a DF with missing weekdays
        mat_df = pd.DataFrame({'date' : pd.date_range(start = df['date'].min(), end = df['date'].max(), freq = 'D') if date_list is None else date_list})
        mat_df = mat_df[~mat_df['date'].dt.weekday.isin([5,6])] if date_list is None else mat_df
        mat_df['date'] = pd.to_datetime(mat_df['date']).dt.date
        # for each stock code
        for stock_code in df[target_col].unique():
            stock_df = df[df[target_col] == stock_code].drop(columns = [target_col])
            mat_df = pd.merge(mat_df, stock_df, on = 'date', how = 'left').rename(columns = {price_col : stock_code})
        mat_df = mat_df.set_index('date')
        return mat_df

    def remove_invalid_data(df : pd.DataFrame, country : str):
        # remove holidays
        if country != 'world':
            hls = []
            for date in df.index:
                if date in holidays.financial_holidays(country.capitalize()):
                    hls.append(date)
            no_holiday_df = df[~df.index.isin(hls)]
        else:
            no_holiday_df = df.copy()

        # fill nan for each stock
        for col in no_holiday_df.columns:
            # Backfilling the variables
            no_holiday_df[col] = no_holiday_df[col].fillna(method = 'bfill').fillna(method = 'ffill')

        # Dropping nan values
        no_holiday_df = no_holiday_df.dropna()

        return no_holiday_df