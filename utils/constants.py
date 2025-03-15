import os

ROOT_DIR = os.path.abspath(os.curdir)
CHROME_DRIVER_PATH = os.path.join(ROOT_DIR, 'drivers')

MARKET_INDICES = {
    '%5EGSPC' : 'S&P 500',
    '%5EAXJO' : 'S&P/ASX 200',
    '%5EATOI' : 'S&P/ASX 100',
    '%5EAORD' : 'ALL ORDINARIES',
    '%5EN225' : 'Nikkei 225',
    '%5EHSI' : 'Hang Seng',
    '%5EFTSE' : 'FTSE 100',
    '%5EDJI' : 'Dow Jones',
    '%5EIXIC' : 'NASDAQ',
    '%5EVNINDEX.VN' : 'Vietnam Index'
}

INDEXES_BY_COUNTRY = {
    'australia' : ['S&P/ASX 200', 'S&P/ASX 100', 'ALL ORDINARIES'],
    'united_states' : ['S&P 500', 'Dow Jones', 'NASDAQ'],
    'vietnam' : ['Vietnam Index'],
    'japan' : ['Nikkei 225'],
    'hong_kong' : ['Hang Seng'],
    'united_kingdom' : ['FTSE 100']

}

COUNTRY_MAPPER = {
    'vietnam' : ['VN', 'Vietnam'],
    'australia' : ['AU', 'Australia'],
    'united_states' : ['US', 'USA', 'United States'],
}

EXCHANGE_MAPPER = {
    'vietnam' : '.VN',
    'australia' : '.AX',
    'united_states' : ''
}

STOCK_EXCHANGE_MAPPER = {
    'vietnam' : 'VN',
    'australia' : 'AU',
    'united_states' : 'US' 
}

CURRENCY_MAPPER = {
    'australia' : 'aud',
    'vietnam' : 'vnd',
    'united_states' : 'usd'
}

PLOTLY_CURRENCY_NORMALIZER = {
    'vnd' : 1000,
    'usd' : 1,
    'aud' : 1
}

CURRENCIES = ['VND', 'AUD', 'JPY', 'HKD', 'GBP']

COMMSEC_SHARE_FEE = {
    1000 : 5,
    3000 : 10,
    10000 : 19.95,
    25000 : 29.95,
}
COMMSEC_SHARE_LARGE_FEE_PERCENTAGE = 0.0012

COMMSEC_POCKET_FEE = {
    1000 : 2,
}
COMMSEC_POCKET_LARGE_FEE_PERCENTAGE = 0.002

EODHD_EXCHANGE_CODES_URL = 'https://eodhd.com/api/exchanges-list/?api_token={}&fmt=json'
EODHD_TICKERS_URL = 'https://eodhd.com/api/exchange-symbol-list/{}?api_token={}&fmt=json'
EODHD_HISTORICAL_STOCK_URL = 'https://eodhd.com/api/eod/{}.{}?period=d&api_token={}&fmt=json'

DEVAPI_URL = 'https://devapi.ai/api/v1/markets/stock/modules'

ASX_API = 'https://www.asx.com.au/asx/1/share/{}/prices?interval=daily&count={}'