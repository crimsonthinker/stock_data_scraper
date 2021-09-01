import os
from datetime import datetime
from sqlalchemy import text

from utils.utilities import get_engine

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd

from utils.constants import *

class HNXStocks(object):
    HNX_STOCK_URL = 'https://www.hsx.vn/Modules/Listed/Web/Symbols'
    HNX_STOCK_LIST_HEADER = [
        'id',
        'stock_code',
        'isin_code',
        'figi_code',
        'listing_business',
        'listing_volume',
        'fee_float',
        'listing_date'
    ]
    def __init__(self, headless = True):
        self._stock_table_id = 'gview_symbols-grid' #table
        self._content_id = 'symbols-grid' #table content
        self._page_navigator = 'DbGridPager_1'

        self._browser_option = webdriver.ChromeOptions()
        if headless:
            self._browser_option.add_argument('headless')
        self._browser_option.add_argument('no-sandbox')
        self._browser_option.add_argument('disable-dev-shm-usage')
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
        #HNX run using JQuery -> need to wait until all JQuery finish loading
        WebDriverWait(self._driver, 10).until(lambda d: d.execute_script("return jQuery.active == 0"))
        #find main tabel
        self._stock_table = self._driver.find_element_by_id(self._stock_table_id)
        self._soup = BeautifulSoup(self._stock_table.get_attribute('innerHTML'), 'html.parser')

    def _get_company_data(self):
        self._extract_soup()
        current_page = 1
        df = pd.DataFrame(columns = ['company_name', 'free_float', 'first_transaction_date', 'stock_code', 'listing_volume', 'stock_exchange'])
        while True: #Need to change because the data is limited
            # find table
            table = self._soup.find("table", {'id' : self._content_id})
            # for each row
            for row in table.find_all('tr', {'role' : 'row'})[1:]:
                #extract cells to get company's information
                cells = row.find_all('td', {'role' : 'gridcell'})
                company = {name : cell.getText() for name, cell in zip(HNXStocks.HNX_STOCK_LIST_HEADER, cells)}
                df.loc[-1] = [
                    company['listing_business'],
                    int(float(company['fee_float'].replace('.','').replace(',','.'))),
                    datetime.strptime(company['listing_date'], '%d/%m/%Y'),
                    company['stock_code'],
                    int(float(company['listing_volume'].replace('.','').replace(',','.'))),
                    'HSX'
                ]
                df.index = df.index + 1  # shifting index

            # find pages
            pages = self._driver.find_element_by_id(self._page_navigator)
            current_page += 1
            try:
                next_page_button = pages.find_element_by_xpath(f"//a[text()='{str(current_page)}']")
            except:
                # there's no page -> finish crawling
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
        self._driver.get(HNXStocks.HNX_STOCK_URL)

        # step 2: Get number of pages
        self._get_company_data()

if __name__ == '__main__':
    hs = HNXStocks()
    hs.work()