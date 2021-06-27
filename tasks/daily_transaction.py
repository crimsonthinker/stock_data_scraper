from datetime import datetime, time, timedelta
import urllib.request
import os
import zipfile
import pandas as pd
import shutil
from sqlalchemy import text
from sqlalchemy import exc
from utils.utilities import *
from urllib.error import HTTPError, URLError


class DailyTransaction(object):
    EOD_TRANSACTION_FORMAT_URL = 'https://images1.cafef.vn/data/{}/CafeF.SolieuGD.{}.zip'
    UP_TO_TRANSACTION_FORMAT_URL = 'https://images1.cafef.vn/data/{}/CafeF.SolieuGD.Upto{}.zip'
    EOD_FILE_FORMAT = 'CafeF.{}.{}.{}.{}.csv'
    UPTO_FILE_FORMAT = 'CafeF.{}.Upto{}.{}.{}.csv'
    EOD_INDEX_FORMAT_URL = 'https://images1.cafef.vn/data/{}/CafeF.Index.{}.zip'
    UPTO_INDEX_FORMAT_URL = 'https://images1.cafef.vn/data/{}/CafeF.Index.Upto{}.zip'
    EOD_INDEX_FILE_FORMAT_URL = 'CafeF.INDEX.{}.{}.{}.csv'
    UPTO_INDEX_FILE_FORMAT_URL = 'CafeF.INDEX.Upto{}.{}.{}.csv'
    ROOT_PATH = '.cache'
    def __init__(self):
        self.engine = get_engine()
        self.schema = 'public'
        self.table = 'transaction'
        self.index_table = 'stock_index'

    def _crawl_index(self, date, mode = 'eod'):
        today_format_1 = date.strftime('%Y%m%d')
        today_format_2 = date.strftime('%d%m%Y')
        save_path = os.path.join('.cache', f'{today_format_1}.zip')

        # download file as zip
        if mode == 'eod':
            transaction_url = DailyTransaction.EOD_INDEX_FORMAT_URL.format(today_format_1, today_format_2)
        else:
            transaction_url = DailyTransaction.UPTO_INDEX_FORMAT_URL.format(today_format_1, today_format_2)
        
        try:
            with urllib.request.urlopen(transaction_url) as dl_file:
                with open(save_path, 'wb') as f:
                    f.write(dl_file.read())
        except HTTPError as err:
            if err.code == 404:
                print(f"Probably due to non-existed data or data from day {date} has not been updated yet. Skipping the date")
                return False
            else:
                raise URLError(f"Encountered HTTP error: {err.code}")
            
        #extract file to folder
        zip_folder = os.path.join('.cache', today_format_1)
        with zipfile.ZipFile(save_path, 'r') as zip_ref:
            zip_ref.extractall(zip_folder)

        # for each stock exchanges, read and save to postgresql database
        if mode == 'eod':
            print(f"Updating data for date {date}")
        else:
            print(f"Updating data for date {date} and previous days")
        day = str(date.day).zfill(2)
        month = str(date.month).zfill(2)
        year = date.year
        if mode == 'eod':
            file_path = DailyTransaction.EOD_INDEX_FILE_FORMAT_URL.format(day, month, year)
        else:
            file_path = DailyTransaction.EOD_INDEX_FILE_FORMAT_URL.format(day, month, year)
        file_path = os.path.join(zip_folder, file_path)
        df = pd.read_csv(file_path)
        #rename columns
        df = df.rename(columns = {
            '<Ticker>' : 'stock_index',
            '<DTYYYYMMDD>' : 'date',
            '<Open>' : 'open_price',
            '<High>' : 'highest_price',
            '<Low>' : 'lowest_price',
            '<Close>' : 'close_price',
            '<Volume>' : 'volume'
        })
        df['date'] = df['date'].apply(str)
        df['date'] = pd.to_datetime(df['date'])

        for index, row in df.iterrows():
            query = text(f""" 
                INSERT INTO {self.schema}.{self.index_table}
                VALUES ( 
                    '{row["stock_index"]}', 
                    '{row["date"].strftime('%Y-%m-%d')}',
                    {row["open_price"]},
                    {row["highest_price"]},
                    {row["lowest_price"]},
                    {row["close_price"]},
                    {row["volume"]}
                )
                ON CONFLICT ON CONSTRAINT stock_index_unique_key DO NOTHING;""")
            self.engine.execute(query)
            print(f"Index: {index + 1} rows updated")
        return True

    def _crawl(self, date, mode = 'eod'):
        today_format_1 = date.strftime('%Y%m%d')
        today_format_2 = date.strftime('%d%m%Y')
        save_path = os.path.join('.cache', f'{today_format_1}.zip')

        # download file as zip
        if mode == 'eod':
            transaction_url = DailyTransaction.EOD_TRANSACTION_FORMAT_URL.format(today_format_1, today_format_2)
        else:
            transaction_url = DailyTransaction.UP_TO_TRANSACTION_FORMAT_URL.format(today_format_1, today_format_2)
        
        try:
            with urllib.request.urlopen(transaction_url) as dl_file:
                with open(save_path, 'wb') as f:
                    f.write(dl_file.read())
        except HTTPError as err:
            if err.code == 404:
                print(f"Probably due to non-existed data or data from day {date} has not been updated yet. Skipping the date")
                return False
            else:
                raise URLError(f"Encountered HTTP error: {err.code}")
            
        #extract file to folder
        zip_folder = os.path.join('.cache', today_format_1)
        with zipfile.ZipFile(save_path, 'r') as zip_ref:
            zip_ref.extractall(zip_folder)

        # for each stock exchanges, read and save to postgresql database
        if mode == 'eod':
            print(f"Updating data for date {date}")
        else:
            print(f"Updating data for date {date} and previous days")
        stock_exchanges = ['HNX', 'HSX', 'UPCOM']
        for stock_exchange in stock_exchanges:
            day = str(date.day).zfill(2)
            month = str(date.month).zfill(2)
            year = date.year
            if mode == 'eod':
                file_path = DailyTransaction.EOD_FILE_FORMAT.format(stock_exchange, day, month, year)
            else:
                file_path = DailyTransaction.UPTO_FILE_FORMAT.format(stock_exchange, day, month, year)
            file_path = os.path.join(zip_folder, file_path)
            df = pd.read_csv(file_path)
            #rename columns
            df = df.rename(columns = {
                '<Ticker>' : 'stock_code',
                '<DTYYYYMMDD>' : 'date',
                '<Open>' : 'open_price',
                '<High>' : 'highest_price',
                '<Low>' : 'lowest_price',
                '<Close>' : 'close_price',
                '<Volume>' : 'volume'
            })
            df['stock_exchange'] = stock_exchange
            df['date'] = df['date'].apply(str)
            df['date'] = pd.to_datetime(df['date'])

            # perform update on row
            for index, row in df.iterrows():
                query = text(f""" 
                    INSERT INTO {self.schema}.{self.table}
                    VALUES (
                        '{stock_exchange}', 
                        '{row["stock_code"]}', 
                        '{row["date"].strftime('%Y-%m-%d')}',
                        {row["open_price"]},
                        {row["highest_price"]},
                        {row["lowest_price"]},
                        {row["close_price"]},
                        {row["volume"]}
                    )
                    ON CONFLICT ON CONSTRAINT transaction_unique_key DO NOTHING;""")
                try:
                    self.engine.execute(query)
                except exc.IntegrityError:
                    print(f"Foreign key constraint. Stock code {row['stock_code']} removed due to violation")
                    continue
                print(f"{stock_exchange}: {index + 1} rows updated")

        return True

    def work(self):
        if os.path.exists(DailyTransaction.ROOT_PATH):
            shutil.rmtree(DailyTransaction.ROOT_PATH)
        os.makedirs(DailyTransaction.ROOT_PATH)

        # get maximum date from the table
        query = f"SELECT MAX(date) FROM {self.schema}.{self.table}"
        df = pd.read_sql_query(query, self.engine)
        if df['max'].iloc[0] is None: # first time initializing the table -> no content -> need to crawl data from up to today
            end_date = datetime.today()
            found_last_updated_day = False
            #TODO: This may fall into infinite loops -> There should be a condition to stop this
            while not found_last_updated_day:
                found_last_updated_day = self._crawl(end_date, mode = 'upto')
                if not found_last_updated_day:
                    end_date = end_date - timedelta(days = 1)

            end_date = datetime.today()
            found_last_updated_day = False
            while not found_last_updated_day:
                found_last_updated_day = self._crawl_index(end_date, mode = 'upto')
                if not found_last_updated_day:
                    end_date = end_date - timedelta(days = 1)
        else:
            begin_date = df['max'].iloc[0]
            end_date = datetime.today().date()
            while begin_date < end_date:
                # change to next day and begin crawling data
                begin_date = begin_date + timedelta(days = 1)
                self._crawl(begin_date)
                self._crawl_index(begin_date)



if __name__ == '__main__':
    ds = DailyTransaction()
    ds.work()

        
            

