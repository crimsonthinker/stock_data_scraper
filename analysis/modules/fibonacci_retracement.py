import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from dateutil.relativedelta import relativedelta
from datetime import timedelta
import matplotlib
import matplotlib.dates as mdates

from utils.utilities import get_engine

def fibonacci_retracement_strategy(stock_code : str, day_interval : int = 252):
    """A Fibonacci retracement approach

    Args:
        stock_code (str): stock code
        day_interval (int, optional): interval of transaction day. Defaults to 252.
    """

    engine = get_engine()
    # we only need 2 to 3 days to analyze candlestick
    end_date = datetime.today().date()
    start_date = end_date - relativedelta(days = day_interval)

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
    df = pd.read_sql_query(query, engine)
    df.reset_index(drop = True, inplace = True) # to make sure that loc and iloc is the same

    # calculate highest and lowest swing
    highest_swing_idx = -1
    lowest_swing_idx = -1
    for i in range(1, len(df) - 1):
        if df.loc[i, 'highest_price'] > df.loc[i - 1, 'highest_price'] and \
            df.loc[i, 'highest_price'] > df.loc[i + 1, 'highest_price'] and \
                (highest_swing_idx == -1 or df.loc[i, 'highest_price'] > df.loc[highest_swing_idx, 'highest_price']):
                highest_swing_idx = i

        if df.loc[i, 'lowest_price'] < df.loc[i - 1, 'lowest_price'] and \
            df.loc[i, 'lowest_price'] < df.loc[i + 1, 'lowest_price'] and \
                (lowest_swing_idx == -1 or df.loc[i, 'lowest_price'] < df.loc[lowest_swing_idx, 'lowest_price']):
                lowest_swing_idx = i

    beautiful_ratios = [0.0, 0.236, 0.5, 0.618, 0.786, 1.0]
    colors = ["black","red","green","blue","cyan","magenta","yellow"]
    levels = []


    # calculate levels
    max_level = df.loc[highest_swing_idx, 'highest_price']
    min_level = df.loc[lowest_swing_idx, 'lowest_price']

    for ratio in beautiful_ratios:
        if highest_swing_idx > lowest_swing_idx: # Uptrend
            levels.append(max_level - (max_level - min_level) * ratio)
        else: #Downtrend
            levels.append(min_level + (max_level - min_level) * ratio)

    # plot level
    plt.rcParams['figure.figsize'] = [12, 7]
    plt.rc('font', size=14)

    dates = [datetime.combine(x, datetime.min.time()) for x in df['date']]
    plt.xlim([dates[0], dates[-1]])
    plt.plot(df['date'], df['close_price'])
    plt.gcf().autofmt_xdate()

    start_idx = df.index[min(highest_swing_idx, lowest_swing_idx)]
    end_idx = df.index[max(highest_swing_idx, lowest_swing_idx)]

    for i in range(len(levels)):
        plt.hlines(
            levels[i], 
            df.loc[start_idx]['date'], 
            df.loc[end_idx]['date'], 
            label = "{:.1f}%".format(beautiful_ratios[i] * 100),
            colors=colors[i], 
            linestyles="dashed"
        )

    plt.legend()
    plt.show()

    return df

if __name__ == '__main__':
    fibonacci_retracement_strategy('BVH', 360)

    