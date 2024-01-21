import pandas as pd
import matplotlib.pyplot as plt

from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import List
import math
from plotly.subplots import make_subplots
import plotly.graph_objects as go

from utils.utilities import get_engine

def fibonacci_retracement_strategy(
    stock_codes : List[str],
    country = 'AU', 
    days : int = 365,
    ):
    """A Fibonacci retracement approach

    Args:
        stock_code (str): stock code
        day_interval (int, optional): interval of transaction day. Defaults to 252.
    """

    # Fibonacci ratios
    beautiful_ratios = [0.0, 0.236, 0.5, 0.618, 0.786, 1.0]
    colors = ["black","red","green","blue","cyan","magenta","yellow"]

    engine = get_engine(country = country)
    # we only need 2 to 3 days to analyze candlestick
    end_date = datetime.today().date()
    start_date = end_date - relativedelta(days = days)

    fig = make_subplots(math.ceil(len(stock_codes) / 2), 2)
    for num,stock_code in enumerate(stock_codes):
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
        df = pd.read_sql_query(query, engine)
        
        df.index = df['date']
        df = df.drop('date', axis = 1)

        # Remove nan value
        df = df.dropna()
        # calculate highest and lowest swing
        highest_swing_idx = -1
        lowest_swing_idx = -1
        for i in range(1, len(df) - 1):
            if df.iloc[i]['high'] > df.iloc[i - 1]['high'] and \
                df.iloc[i]['high'] > df.iloc[i + 1]['high'] and \
                    (highest_swing_idx == -1 or df.iloc[i]['high'] > df.iloc[highest_swing_idx]['high']):
                    highest_swing_idx = i

            if df.iloc[i]['low'] < df.iloc[i - 1]['low'] and \
                df.iloc[i]['low'] < df.iloc[i + 1]['low'] and \
                    (lowest_swing_idx == -1 or df.iloc[i]['low'] < df.iloc[lowest_swing_idx]['low']):
                    lowest_swing_idx = i
        levels = []


        # calculate levels
        max_level = df.iloc[highest_swing_idx]['high']
        min_level = df.iloc[lowest_swing_idx]['low']

        for ratio in beautiful_ratios:
            if highest_swing_idx > lowest_swing_idx: # Uptrend
                levels.append(max_level - (max_level - min_level) * ratio)
            else: #Downtrend
                levels.append(min_level + (max_level - min_level) * ratio)

        fig.add_trace(go.Scatter(x = df.index, y = df['close'], name = stock_code), row = int(num / 2) + 1, col = int(num % 2) + 1)

        # # Add upper and lower band
        # fig.add_trace(go.Scatter(x=df.index.to_list(),
        #     y=df['high'],
        #     showlegend=False,
        #     color='black'
        # ),
        #     row = int(num / 2) + 1, col = int(num % 2) + 1
        # )

        # fig.add_trace(go.Scatter(x=df.index[::-1].to_list(),
        #     y = df['low'][::-1],
        #     showlegend=False,
        #     color='black'),
        #     row = int(num / 2) + 1, col = int(num % 2) + 1
        # )


        fig.update_xaxes(range=[df.index[0], df.index[-1]], row = int(num / 2) + 1, col = int(num % 2) + 1)

        for i in range(len(levels)):
            fig.add_hline(
                y = levels[i],
                line_dash='dot',
                line_color=colors[i],
                row = int(num / 2) + 1, col = int(num % 2) + 1
            )
    fig.update_layout(height = 800)
    fig.show()

if __name__ == '__main__':
    fibonacci_retracement_strategy('SYI', 360)

    