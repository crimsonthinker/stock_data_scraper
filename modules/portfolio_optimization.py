import numpy as np
import pandas as pd
from typing import List, Dict
import matplotlib.pyplot as plt
from utils.data_utils import StockPriceProcess
from datetime import datetime
from dateutil.relativedelta import relativedelta
import cvxpy as cp

from pypfopt.efficient_frontier import EfficientFrontier
import pypfopt
from pypfopt import objective_functions
from pypfopt import plotting as ef_plotting

from utils.generic_utils import SQLModule
from utils.constants import CURRENCY_MAPPER
from utils.risk_free_rates import RiskFreeRate

def ef(
    indexes : Dict[str, List[str]], 
    df : pd.DataFrame,
    return_method : str = 'mean_historical_return',
    risk_method : str = 'ledoit_wolf',
    portfolio_method : str = 'optimal',
    risk_threshold : float = 0.2,
):
    # Get expected returns
    expected_returns = pypfopt.expected_returns.return_model(df, method = return_method)
    # Get risk for each stock
    cov_matrix = pypfopt.risk_models.risk_matrix(df, method = risk_method)

    # create EfficientFrontier
    ef = EfficientFrontier(expected_returns = expected_returns, cov_matrix = cov_matrix, solver = cp.ECOS)
    ef.add_objective(objective_functions.L2_reg, gamma = 1)
    

    # plot the efficient frontier first
    _, ax = plt.subplots(figsize=(10, 7))
    ef_plotting.plot_efficient_frontier(ef, ax = ax, show_assets = True)
    # Generate random portfolios
    n_samples = 10000
    w = np.random.dirichlet(np.ones(len(expected_returns)), n_samples)
    rets = w.dot(expected_returns)
    stds = np.sqrt(np.diag(w @ cov_matrix @ w.T)) # convential matrix operator

    # Getting risk free rate for each market indexes
    risk_free_rate = []
    for country in indexes:
        for col in df.columns:
            if col in indexes[country]:
                risk_free_rate.append(RiskFreeRate.mapper[country]())
    # average them
    risk_free_rate = sum(risk_free_rate) / len(risk_free_rate)

    # Color of portfolio importance
    sharpes = (rets - risk_free_rate) / stds
    ax.scatter(stds, rets, marker=".", c=sharpes, cmap="viridis_r")

    ret_tangent, std_tangent, _ = ef.portfolio_performance(risk_free_rate = risk_free_rate)
    ax.scatter(std_tangent, ret_tangent, marker="*", s=100, c="r", label="Max Sharpe")

    # Output
    ax.set_title("Efficient Frontier with random portfolios")
    ax.legend()
    plt.tight_layout()
    plt.show()

    if portfolio_method == 'optimal':
        # Compute other portfolios
        max_clean_weights = ef.clean_weights()
        opt_w = np.array(list(max_clean_weights.values()))
        opt_ret = (opt_w * expected_returns.values).sum()
        return max_clean_weights, opt_ret , stds[np.abs(stds - opt_ret).argmin()]
    elif portfolio_method == 'risk_based':
        filter_idx = np.where(stds <= risk_threshold)[0]
        threshold_w = w[filter_idx,:]
        threshold_rets = rets[filter_idx]
        threshold_stds = stds[filter_idx]
        opt_w = threshold_w[np.argmax(threshold_rets),:]
        total = np.exp(opt_w).sum()
        return {s : np.exp(opt_w[k]) / total for k,s in enumerate(expected_returns.index)}, np.amax(threshold_rets), threshold_stds[np.argmax(threshold_rets)]

def ef_world_portfolio(
        indexes : Dict[str, List[str]], 
        return_method : str = 'mean_historical_return',
        risk_method : str = 'ledoit_wolf',
        portfolio_method : str = 'optimal',
        risk_threshold : float = 0.2,
        days : int = 365
    ):
    """Calculate portfolio from multiple countries using their indexes

    Args:
        indexes (Dict[str, List[str]]): A dictionary, with:
            - key as the country, and
            - value as a list of marker indexes within the country
        return_method (str, optional): _description_. Defaults to 'mean_historical_return'.
        risk_method (str, optional): _description_. Defaults to 'ledoit_wolf'.
        portfolio_method (str, optional): _description_. Defaults to 'optimal'.
        risk_threshold (float, optional): _description_. Defaults to 0.2.
        days (int, optional): _description_. Defaults to 365.

    Returns:
        _type_: _description_
    """    
    engine = SQLModule.get_engine(country = 'world')

    # Get date based on period
    end_date = datetime.today().date()
    # Adding one day to calculate pct_change
    start_date = end_date - relativedelta(days = days)

    # Query market indexes
    flat_indexes = []
    for country in indexes:
        flat_indexes = flat_indexes + indexes[country]


    query = f"""
        SELECT
            stock_index,
            date,
            close
        FROM stock_indexes
        WHERE
            stock_index IN {tuple(flat_indexes)}
            AND
            date >= DATE '{start_date}'
            AND
            date <= DATE '{end_date}'
        ORDER BY date
    """
    df = pd.read_sql_query(query, engine)
    df = StockPriceProcess.frame_var(df, target_col = 'stock_index')
    df = StockPriceProcess.remove_invalid_data(df, country = country)

    # Convert to USD
    # Get all exchange rate
    query = f"""
        SELECT
            *
        FROM daily_average_exchange_rate_usd_based
        WHERE
            date >= DATE '{start_date}'
            AND
            date <= DATE '{end_date}'
        ORDER BY date
    """
    ex_rate = pd.read_sql_query(query, engine)
    ex_rate.set_index('date', inplace = True)
    # fill nan for each rate
    for col in ex_rate.columns:
        # Backfilling the variables
        ex_rate[col] = ex_rate[col].fillna(method = 'bfill').fillna(method = 'ffill')

    df = df.join(ex_rate)
    for country in CURRENCY_MAPPER:
        if CURRENCY_MAPPER[country] == 'usd':
            continue
        for index in indexes[country]:
            df[index] = df[index] / df[CURRENCY_MAPPER[country]]
    df.drop(columns = ex_rate.columns, inplace = True)

    return ef(
        indexes, 
        df,
        return_method,
        risk_method,
        portfolio_method,
        risk_threshold,
    )

def ef_random_portfolio(
        codes : Dict[str, List[str]] = None,
        return_method : str = 'mean_historical_return',
        risk_method : str = 'ledoit_wolf',
        portfolio_method : str = 'optimal',
        risk_threshold : float = 0.2,
        days : int = 365,
    ):
    

    # Get date based on period
    end_date = datetime.today().date()
    # Adding one day to calculate pct_change
    start_date = end_date - relativedelta(days = days)

    # Query stock data
    df = None
    for country in codes:
        engine = SQLModule.get_engine(country = country)
        query = f"""
            SELECT
                stock_code,
                date,
                close
            FROM transaction
            WHERE
                stock_code IN {tuple(codes[country]) if len(codes[country]) > 1 else "('" + codes[country][0] + "')"}
                AND
                date >= DATE '{start_date}'
                AND
                date <= DATE '{end_date}'
            ORDER BY date
        """
        df = pd.concat([df, pd.read_sql_query(query, engine)])
    df = StockPriceProcess.frame_var(df, target_col = 'stock_code' if country != 'world' else 'stock_index')
    df = StockPriceProcess.remove_invalid_data(df, country = country)

    # Convert to USD
    # Get all exchange rate
    engine = SQLModule.get_engine(country = 'world')
    query = f"""
        SELECT
            *
        FROM daily_average_exchange_rate_usd_based
        WHERE
            date >= DATE '{start_date}'
            AND
            date <= DATE '{end_date}'
        ORDER BY date
    """
    ex_rate = pd.read_sql_query(query, engine)
    ex_rate.set_index('date', inplace = True)
    # fill nan for each stock
    for col in ex_rate.columns:
        # Backfilling the variables
        ex_rate[col] = ex_rate[col].fillna(method = 'bfill').fillna(method = 'ffill')

    # merge with df
    df = df.join(ex_rate)
    for country in CURRENCY_MAPPER:
        if CURRENCY_MAPPER[country] == 'usd':
            continue
        for index in codes[country]:
            df[index] = df[index] / df[CURRENCY_MAPPER[country]]

    df.drop(columns = ex_rate.columns, inplace = True)

    return ef(
        codes, 
        df,
        return_method,
        risk_method,
        portfolio_method,
        risk_threshold,
    )