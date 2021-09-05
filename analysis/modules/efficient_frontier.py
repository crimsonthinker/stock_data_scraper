import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.optimize as sco
import copy

def portfolio_annualised_performance(
    weights : np.ndarray, 
    mean_returns : np.array, 
    cov_matrix : np.ndarray,
    days : int):
    """Return the portfolio

    Args:
        weights (np.ndarray): a 1-d array of weights
        mean_returns (np.ndarray): a 1-d array of mean returns of stocks
        cov_matrix (np.ndarray): covariance matrix of stocks

    Returns:
        [type]: [description]
    """
    returns_portfolio = np.sum(mean_returns * weights) * days
    std_portfolio = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(days)
    return std_portfolio, returns_portfolio

def portfolio_volatility(
    weights : np.ndarray, 
    mean_returns : np.ndarray, 
    cov_matrix : np.ndarray,
    days : int):
    return portfolio_annualised_performance(weights, mean_returns, cov_matrix, days)[0]

def neg_sharpe_ratio(
    weights : np.ndarray, 
    mean_returns : np.ndarray, 
    cov_matrix : np.ndarray, 
    risk_free_rate : float,
    days : int):
    p_var, p_ret = portfolio_annualised_performance(weights, mean_returns, cov_matrix, days)
    return -(p_ret - risk_free_rate) / p_var

def max_sharpe_ratio(
    num_of_stocks : int,
    mean_returns : np.ndarray, 
    cov_matrix : np.ndarray, 
    risk_free_rate : float,
    days : int):
    args = (mean_returns, cov_matrix, risk_free_rate, days)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bound = (0.0,1.0)
    bounds = tuple(bound for _ in range(num_of_stocks))
    result = sco.minimize(
        neg_sharpe_ratio, 
        num_of_stocks*[1./num_of_stocks,], 
        args=args,
        method='SLSQP', 
        bounds=bounds, 
        constraints=constraints)
    return result

def min_variance(
    num_of_stocks : int,
    mean_returns : np.ndarray, 
    cov_matrix : np.ndarray,
    days : int):
    args = (mean_returns, cov_matrix, days)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bound = (0.0,1.0)
    bounds = tuple(bound for asset in range(num_of_stocks))

    result = sco.minimize(
        portfolio_volatility, 
        num_of_stocks*[1./num_of_stocks,], 
        args=args,
        method='SLSQP', 
        bounds=bounds, 
        constraints=constraints)

    return result

def efficient_return(
    num_of_stocks : int,
    mean_returns : np.ndarray, 
    cov_matrix : np.ndarray, 
    days : int,
    target : float):
    args = (mean_returns, cov_matrix, days)

    def portfolio_return(weights):
        return portfolio_annualised_performance(weights, mean_returns, cov_matrix, days)[1]

    constraints = ({'type': 'eq', 'fun': lambda x: portfolio_return(x) - target},
                   {'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0,1) for _ in range(num_of_stocks))
    result = sco.minimize(
        portfolio_volatility, 
        num_of_stocks*[1./num_of_stocks,], 
        args=args, 
        method='SLSQP', 
        bounds=bounds, 
        constraints=constraints)
    return result

def efficient_frontier(
    num_of_stocks : int,
    mean_returns : np.ndarray, 
    cov_matrix : np.ndarray, 
    returns_range : np.ndarray,
    days : int):
    efficients = []
    for ret in returns_range:
        efficients.append(efficient_return(num_of_stocks,mean_returns, cov_matrix, days, ret))
    return efficients


def random_portfolios(
    num_of_stocks : int,
    mean_returns : np.ndarray,
    cov_matrix : np.ndarray,
    num_portfolios : int,
    risk_free_rate : float,
    days : int):
    results = np.zeros((num_portfolios, 3))
    weights_record = []
    for i in range(num_portfolios):
        # Generate random weights
        weights = np.random.random(num_of_stocks)
        weights /= np.sum(weights)
        weights_record.append(weights)

        portfolio_std_dev, portfolio_return = portfolio_annualised_performance(weights, mean_returns, cov_matrix, days)
        results[i, 0] = portfolio_std_dev # std
        results[i, 1] = portfolio_return # mean
        results[i, 2] = (portfolio_return - risk_free_rate) / portfolio_std_dev #sharpe ratio

    return results, weights_record

def display_simulated_ef_with_random(
    close_data : pd.DataFrame, 
    num_portfolios : int, 
    risk_free_rate : float):
    # calculate covariance matrix and mean returns of stock
    # sample them first
    # get daily mean return
    candidates = close_data.columns
    mean_returns = np.zeros((len(candidates),))
    returns = close_data.pct_change()
    returns = returns.fillna(0.0).replace(np.inf, 1.0).replace(-np.inf,-1.0)
    for t,stock_code in enumerate(returns.columns):
        mean_returns[t] = returns[stock_code].mean()
    cov_matrix = close_data.cov()
    results, weights = random_portfolios(
        len(candidates),
        mean_returns, 
        cov_matrix, 
        num_portfolios, 
        risk_free_rate, 
        len(close_data))
    
    max_sharpe_idx = np.argmax(results[:,2])
    sdp, rp = results[max_sharpe_idx, 0], results[max_sharpe_idx, 1]
    max_sharpe_allocation = pd.DataFrame(copy.deepcopy(weights[max_sharpe_idx]),index = candidates,columns=['allocation'])
    max_sharpe_allocation['allocation'] = [round(i*100,2)for i in max_sharpe_allocation['allocation']]
    max_sharpe_allocation = max_sharpe_allocation.T
    
    min_vol_idx = np.argmin(results[:,0]) # minimum volatility
    sdp_min, rp_min = results[min_vol_idx, 0], results[min_vol_idx, 1]
    min_vol_allocation = pd.DataFrame(copy.deepcopy(weights[min_vol_idx]),index = candidates,columns = ['allocation'])
    min_vol_allocation['allocation'] = [round(i*100,2) for i in min_vol_allocation['allocation']]
    min_vol_allocation = min_vol_allocation.T

    print("-"*80)
    print("Maximum Sharpe Ratio Portfolio Allocation\n")
    print("Annualised Return:", round(rp,2))
    print("Annualised Volatility:", round(sdp,2))
    print("\n")
    print(max_sharpe_allocation)
    print("-"*80)
    print("Minimum Volatility Portfolio Allocation\n")
    print("Annualised Return:", round(rp_min,2))
    print("Annualised Volatility:", round(sdp_min,2))
    print("\n")
    print(min_vol_allocation)
    
    plt.figure(figsize=(10, 7))
    plt.scatter(results[:,0],results[:,1],c=results[:,2],cmap='YlGnBu', marker='o', s=10, alpha=0.3)
    plt.colorbar()
    plt.scatter(sdp,rp,marker='*',color='r',s=500, label='Maximum Sharpe ratio')
    plt.scatter(sdp_min,rp_min,marker='*',color='g',s=500, label='Minimum volatility')
    plt.title('Simulated Portfolio Optimization based on Efficient Frontier')
    plt.xlabel('annualised volatility')
    plt.ylabel('annualised returns')
    plt.legend(labelspacing=0.8)

def display_calculated_ef_with_random(
    close_data : pd.DataFrame, 
    num_portfolios : int, 
    risk_free_rate : float):
    candidates = close_data.columns
    mean_returns = np.zeros((len(candidates),))
    returns = close_data.pct_change()
    returns = returns.fillna(0.0).replace(np.inf, 1.0).replace(-np.inf,-1.0)
    for t,stock_code in enumerate(returns.columns):
        mean_returns[t] = returns[stock_code].mean()
    cov_matrix = close_data.cov()

    results, _ = random_portfolios(
        len(candidates),
        mean_returns, 
        cov_matrix, 
        num_portfolios, 
        risk_free_rate, 
        len(close_data))
    
    max_sharpe = max_sharpe_ratio(len(candidates), mean_returns, cov_matrix, risk_free_rate, len(close_data))
    sdp, rp = portfolio_annualised_performance(max_sharpe['x'], mean_returns, cov_matrix, len(close_data))
    max_sharpe_allocation = pd.DataFrame(max_sharpe['x'],index = candidates,columns=['allocation'])
    max_sharpe_allocation.allocation = [round(i*100,2)for i in max_sharpe_allocation.allocation]
    max_sharpe_allocation = max_sharpe_allocation.T

    min_vol = min_variance(len(candidates), mean_returns, cov_matrix, len(close_data))
    sdp_min, rp_min = portfolio_annualised_performance(min_vol['x'], mean_returns, cov_matrix, len(close_data))
    min_vol_allocation = pd.DataFrame(min_vol['x'],index = candidates, columns=['allocation'])
    min_vol_allocation.allocation = [round(i*100,2)for i in min_vol_allocation.allocation]
    min_vol_allocation = min_vol_allocation.T
    
    print("-"*80)
    print("Maximum Sharpe Ratio Portfolio Allocation\n")
    print("Annualised Return:", round(rp,2))
    print("Annualised Volatility:", round(sdp,2))
    print("\n")
    print(max_sharpe_allocation)
    print("-"*80)
    print("Minimum Volatility Portfolio Allocation\n")
    print("Annualised Return:", round(rp_min,2))
    print("Annualised Volatility:", round(sdp_min,2))
    print("\n")
    print(min_vol_allocation)
    
    plt.figure(figsize=(10, 7))
    plt.scatter(results[:,0],results[:,1],c=results[:,2],cmap='YlGnBu', marker='o', s=10, alpha=0.3)
    plt.colorbar()
    plt.scatter(sdp,rp,marker='*',color='r',s=500, label='Maximum Sharpe ratio')
    plt.scatter(sdp_min,rp_min,marker='*',color='g',s=500, label='Minimum volatility')

    target = np.linspace(rp_min, 0.32, 50)
    efficient_portfolios = efficient_frontier(len(candidates), mean_returns, cov_matrix, target, len(close_data))
    plt.plot([p['fun'] for p in efficient_portfolios], target, linestyle='-.', color='black', label='efficient frontier')
    plt.title('Calculated Portfolio Optimization based on Efficient Frontier')
    plt.xlabel('annualised volatility')
    plt.ylabel('annualised returns')
    plt.legend(labelspacing=0.8)

def display_ef_with_selected(close_data : pd.DataFrame,risk_free_rate : float):
    candidates = close_data.columns
    mean_returns = np.zeros((len(candidates),))
    returns = close_data.pct_change()
    returns = returns.fillna(0.0).replace(np.inf, 1.0).replace(-np.inf,-1.0)
    for t,stock_code in enumerate(returns.columns):
        mean_returns[t] = returns[stock_code].mean()
    cov_matrix = close_data.cov()

    max_sharpe = max_sharpe_ratio(len(candidates), mean_returns, cov_matrix, risk_free_rate, len(close_data))
    sdp, rp = portfolio_annualised_performance(max_sharpe['x'], mean_returns, cov_matrix, len(close_data))
    max_sharpe_allocation = pd.DataFrame(max_sharpe.x,index = candidates,columns=['allocation'])
    max_sharpe_allocation.allocation = [round(i*100,2)for i in max_sharpe_allocation.allocation]
    max_sharpe_allocation = max_sharpe_allocation.T

    min_vol = min_variance(len(candidates), mean_returns, cov_matrix, len(close_data))
    sdp_min, rp_min = portfolio_annualised_performance(min_vol['x'], mean_returns, cov_matrix, len(close_data))
    min_vol_allocation = pd.DataFrame(min_vol.x,index = candidates,columns=['allocation'])
    min_vol_allocation.allocation = [round(i*100,2)for i in min_vol_allocation.allocation]
    min_vol_allocation = min_vol_allocation.T
    
    an_vol = np.std(returns) * np.sqrt(len(close_data))
    an_rt = mean_returns * len(close_data)
    
    print("-"*80)
    print("Maximum Sharpe Ratio Portfolio Allocation\n")
    print("Annualised Return:", round(rp,2))
    print("Annualised Volatility:", round(sdp,2))
    print("\n")
    print(max_sharpe_allocation)
    print("-"*80)
    print("Minimum Volatility Portfolio Allocation\n")
    print("Annualised Return:", round(rp_min,2))
    print("Annualised Volatility:", round(sdp_min,2))
    print("\n")
    print(min_vol_allocation)
    print("-"*80)
    print("Individual Stock Returns and Volatility\n")
    for i, txt in enumerate(candidates):
        print(txt,":","annuaised return",round(an_rt[i],2),", annualised volatility:",round(an_vol[i],2))
    print("-"*80)
    
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.scatter(an_vol,an_rt,marker='o',s=200)

    for i, txt in enumerate(candidates):
        ax.annotate(txt, (an_vol[i],an_rt[i]), xytext=(10,0), textcoords='offset points')
    ax.scatter(sdp,rp,marker='*',color='r',s=500, label='Maximum Sharpe ratio')
    ax.scatter(sdp_min,rp_min,marker='*',color='g',s=500, label='Minimum volatility')

    target = np.linspace(rp_min, 0.34, 50)
    efficient_portfolios = efficient_frontier(len(candidates), mean_returns, cov_matrix, target, len(close_data))
    ax.plot([p['fun'] for p in efficient_portfolios], target, linestyle='-.', color='black', label='efficient frontier')
    ax.set_title('Portfolio Optimization with Individual Stocks')
    ax.set_xlabel('annualised volatility')
    ax.set_ylabel('annualised returns')
    ax.legend(labelspacing=0.8)
