import os
from datetime import datetime
from sqlalchemy import text

from utils.utilities import get_engine

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd

from utils.constants import *

class UPCOMStocks(object):
    UPCOM_STOCK_URL = 'https://hnx.vn/cophieu-etfs/chung-khoan-uc.html'
    def __init__(self, headless = True):
        self._stock_table_id = '_tableDatas' #table
        self._page_navigator = 'd_number_of_page'

        self._browser_option = webdriver.ChromeOptions()
        if headless:
            self._browser_option.add_argument('headless')
        # add driver
        self._driver = webdriver.Chrome(
            os.path.join(CHROME_DRIVER_PATH,"chromedriver"),
            chrome_options = self._browser_option
        )
        self.schema = 'public'
        self.table = 'stock_info'
        self.engine = get_engine()


    def _extract_soup(self):
        """[summary]
        """
        # #HOSE run using JQuery -> need to wait until all JQuery finish loading
        WebDriverWait(self._driver, 10).until(lambda d: d.execute_script("return jQuery.active == 0"))
        #find main tabel
        self._stock_table = self._driver.find_element_by_id(self._stock_table_id)
        self._soup = BeautifulSoup(self._stock_table.get_attribute('innerHTML'), 'html.parser')

    def _get_company_data(self):
        self._extract_soup()
        current_page = 1
        df = pd.DataFrame(columns = ['company_name', 'free_float', 'first_transaction_date', 'stock_code', 'listing_volume', 'stock_exchange'])
        while True: #Need to change because the data is limited
            # leave the first row
            for row in self._soup.find_all('tr', {'role' : 'row'})[1:]:
                #extract cells to get company's information
                cells = row.find_all('td')
                df.loc[-1] = [
                    cells[2].find('a').getText(),
                    int(cells[5].getText().strip().replace('.','')),
                    datetime.strptime(cells[3].getText().strip(), '%d/%m/%Y'),
                    cells[1].find('a').getText().strip(),
                    int(cells[4].getText().strip().replace('.','')),
                    'UPCOM'
                ]
                df.index = df.index + 1  # shifting index

            # find pages
            pages = self._driver.find_element_by_id(self._page_navigator)
            current_page += 1
            # find button
            try:
                next_page_button = pages.find_element_by_id(str(current_page))
            except:
                break
            # click the button and wait for the JQuery to finish
            next_page_button.click()
            #extract the soup
            self._extract_soup()

        for _, row in df.iterrows():
            query = text(f""" 
                INSERT INTO {self.schema}.{self.table}
                VALUES (
                    '{row['company_name']}', 
                    {row['free_float']}, 
                    '{row['first_transaction_date'].strftime('%Y-%m-%d')}',
                    '{row['stock_code']}',
                    {row['listing_volume']},
                    '{row['stock_exchange']}'
                )
                ON CONFLICT ON CONSTRAINT stock_info_pkey
                DO UPDATE SET 
                    (free_float, listing_volume) = (EXCLUDED.free_float, EXCLUDED.listing_volume)
            """)
            self.engine.execute(query)


    def work(self):
        # step 1: Access the link
        self._driver.get(UPCOMStocks.UPCOM_STOCK_URL)

        # step 2: Get number of pages
        self._get_company_data()

if __name__ == '__main__':
    hs = UPCOMStocks()
    hs.work()