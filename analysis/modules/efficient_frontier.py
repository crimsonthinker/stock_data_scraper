import numpy as np
import pandas as pd
from typing import List
import matplotlib.pyplot as plt
from pypfopt.efficient_frontier import EfficientFrontier
import pypfopt
from pypfopt import plotting as ef_plotting
from datetime import datetime, timedelta

from utils.utilities import get_engine

def ef_random_portfolio(stock_codes : List[str],risk_free_rate : float = 0.06, day_interval : int = 260):
    """Calculate portfolio with selected efficient frontier

    Args:
        stock_codes (List[str]): list of stocks
        risk_free_rate (float, optional): risk free rate (from the bank it is 6%). Defaults to 0.06.
        day_interval (int, optional): interval of data. Defaults to 260.
    """
    # Query stock data 
    engine = get_engine()

    # Get 1 year data
    end_date = datetime.today().date()
    start_date = end_date - timedelta(days = day_interval)

    stock_query = f"""
        SELECT
            stock_code,
            date,
            close_price
        FROM public.transaction
        WHERE
            stock_code IN {tuple(stock_codes)}
            AND
            date >= DATE '{start_date}'
            AND
            date <= DATE '{end_date}'
    """
    print("Query data")
    df = pd.read_sql_query(stock_query, engine)

    # Convert to appropriate format, in which columns are stock, rows are date, and each cell is the close_price
    print("Convert data to close format")
    close_data = None
    for stock in stock_codes:
        stock_data = df[df['stock_code'] == stock][['date', 'close_price']]
        stock_data.index = stock_data['date']
        stock_data = stock_data.drop('date', axis = 1).sort_index()
        stock_data = stock_data.rename(columns = {
            'close_price' : stock
        })
        if close_data is None:
            close_data = stock_data
        else:
            close_data = close_data.merge(stock_data, how = 'outer', left_index = True, right_index = True)
    close_data = close_data.fillna(0.0)

    # Begin calculation
    print("Begin calculation")
    stocks = close_data.columns
    mean_returns = np.zeros((len(stocks),))
    returns = close_data.pct_change() # percentage change between the current and prior
    returns = returns.fillna(0.0).replace(np.inf, 1.0).replace(-np.inf,-1.0)

    # Get expected return and cov
    expected_returns = pypfopt.expected_returns.mean_historical_return(close_data)
    cov_matrix = pypfopt.risk_models.sample_cov(close_data)

    # create EfficientFrontier
    ef = EfficientFrontier(
        expected_returns = expected_returns, 
        cov_matrix = cov_matrix,
        )

    # plot the efficient frontier first
    fig, ax = plt.subplots(figsize=(10, 7))
    ef_plotting.plot_efficient_frontier(ef, ax = ax, show_assets = True)

    # Find the tangency portflio

    # Find the tangency portfolio
    max_sharpe_weights = ef.max_sharpe()
    ret_tangent, std_tangent, _ = ef.portfolio_performance(risk_free_rate = risk_free_rate)
    ax.scatter(std_tangent, ret_tangent, marker="*", s=100, c="r", label="Max Sharpe")

    # Generate random portfolios
    n_samples = 10000
    w = np.random.dirichlet(np.ones(len(expected_returns)), n_samples)
    rets = w.dot(expected_returns)
    stds = np.sqrt(np.diag(w @ cov_matrix @ w.T)) # convential matrix operator
    sharpes = rets / stds
    ax.scatter(stds, rets, marker=".", c=sharpes, cmap="viridis_r")

    # Output
    ax.set_title("Efficient Frontier with random portfolios")
    ax.legend()
    plt.tight_layout()
    plt.show()

    total = sum(list(max_sharpe_weights.values()))

    return {k : max_sharpe_weights[k] / total for k in max_sharpe_weights}