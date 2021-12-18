# A scraper for Vietnamese stock data 

## Introduction
This repository provides a scraper framework to efficiently obtain Vietnamese stock data. It includes a scraper module that is performed daily,
a database design (stored in sql file) to store data, and an analysis module to query and extract the stock data for specific needs.

## Installation
The project runs using Python 3.9.5 and PostGreSQL version 14.0. To install, refer to the following steps:

1. Download chromedrivers for scraper and put executable file to **drivers** folder. Link:
```
https://chromedriver.storage.googleapis.com/index.html?path=92.0.4515.107/
```

Rename extracted file to *chromedrivers*.

2. Create postgres database from db_design.sql. 

The default configuration for the database connection is stored in *conf/db_config.yml*.
If you want to use your own configuration, please modify the above file as well as transferring the owner of the tables (displayed in *db_design.sql*)
to your designated username.

3. Install required libraries for Python:
Using python 3.9.5, install the requirements with:
```
pip install -r requirements.txt
```

3. Run the following commands to update your data daily:
```
python3 -m tasks.hnx_stock_codes
# Scrape information of HNX codes from https://hnx.vn/cophieu-etfs/chung-khoan-ny.html
```

```
python3 -m tasks.hsx_stock_codes
# Scrape information of HSX codes from https://www.hsx.vn/Modules/Listed/Web/Symbols
```

```
python3 -m tasks.upcom_stock_codes
# Scrape information of UPCOM codes from https://hnx.vn/cophieu-etfs/chung-khoan-uc.html
```

```
python3 -m tasks.daily_transaction
# Download data from https://cafef1.mediacdn.vn and parse data to the table.
```
It is recommended that all the first three commands be done before running the last one.

Note that these url links to scrape data are very inconsistent, so updated versions of this repo will be provided when modification is needed.

## Usage

In *analysis* folder, we adopt many libraries (such as [talib](https://mrjbq7.github.io/ta-lib/) and 
[pypfopt](https://pyportfolioopt.readthedocs.io/en/latest/)) to implement different algorithms for stock data analysis, including Bollinger Bands, 
Efficient Frontier, Fibonacci Retracement, and so on. This folder includes *modules* folder, which stores the implementations of the above algorithms,
and *notebook* folder, which consists of examples written in Jupyter Notebook.

Since this is an on-going personal project, there has not been many new features available, so any contribution from other users is welcomed :).