import platform

if platform.system() == "Linux":
    import linux_tools as tools
elif platform.system() == "Windows":
    import windows_tools as tools

import concurrent.futures
import csv
import os
from pathlib import Path
import time

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from contextlib import contextmanager
import sys
sys.path.append(tools.AUTOMATE_TEXTING_PATH)
from automate_texting import send_message

# { time python3 AmazonScraperMultithread.py; } &> res.txt

# Set working directory to project file
os.chdir(os.path.dirname(__file__))
# Define the search function that will locate the desired item

log_path_file_name = f'{time.strftime("%Y-%m-%d")}_Amazon_scraper.log'


@contextmanager
def driver(*args, **kwargs):
    firefox_options = Options()
    # commented this line out because it doesn't work on windows
    # firefox_options.add_argument('--no-sandbox')
    firefox_options.add_argument('--disable-blink-features=AutomationControlled')
    firefox_options.add_argument('--ignore-ssl-errors=yes')
    firefox_options.add_argument('--ignore-certificate-errors')
    firefox_options.add_argument("--disable-infobars")
    firefox_options.add_argument("--disable-extensions")
    firefox_options.add_argument("--disable-popup-blocking")
    firefox_options.add_argument("--headless")

    d = webdriver.Firefox(service=Service(GeckoDriverManager().install(), log_path=f'{tools.LOG_PATH}{log_path_file_name}'), options=firefox_options,)

    try:
        yield d
    finally:
        d.quit()

def search(s):
    general = 'https://www.amazon.com/s?k={}&ref=nb_sb_noss_2'
    new_search = s.replace(' ', '+')
    new = general.format(new_search)
    new += '&page={}'
    return new

# Create an extraction model that will retrieve the desired product information
def extract(item):
    atag = item.h2.a
    description = atag.text.strip()

    url = 'https://www.amazon.com' + atag.get('href')
    try:
        price_parent = item.find('span','a-price')
        price = price_parent.find('span','a-offscreen').text
    except AttributeError:
        return

    try:
        rating = item.i.text
        num_review = item.find('span',{'class': 'a-size-base','dir':'auto'}).text
    except:
        rating = ''
        num_review = 0
    result = (time.strftime("%Y-%m-%d"), description,price,rating,num_review,url)

    return result

# Main program function where the the search and extract functions are used to apply the extraction model to the first 6 pages of amazon.
# The data extracted is formatted and added to a csv file named after the desired product.
def process_query(item):
    with driver() as wd:
        records = []
        url = search(item[0])
        for page in range(1,7):
            wd.get(url.format(page))
            soup = BeautifulSoup(wd.page_source, 'html.parser')
            results = soup.find_all('div',{'data-component-type':"s-search-result"})
            for i in results:
                record = extract(i)
                if record:
                    records.append(record)
        # print(f'records: {records}')
        filePathComplete = "{}/CSVFiles/{}.csv".format(os.getcwd(), item[1])

        with open(filePathComplete, 'a', newline= '', encoding = 'utf-8') as file:
            writer = csv.writer(file)
            if os.stat(filePathComplete).st_size == 0:
                writer.writerow(['Date','Description','Price','Rating','Review Count', 'URL'])
            writer.writerows(records)

def filterCSV(csvFile, keyWord):
    df1 = pd.read_csv(csvFile,index_col=False)
    df1 = df1[df1.Description == keyWord]
    # df1.reset_index(inplace=True, drop=True)
    # print(df1)
    df1.to_csv(csvFile, index=False,)
    # print(pd.read_csv(io.StringIO(df1.to_csv(index=False)),).columns)

def main():
    lastDate = ''
    if not os.path.isfile(f'{os.getcwd()}/time_stamp.txt'):
        with open(f'{os.getcwd()}/time_stamp.txt', 'w') as f:
            f.write('')
    with open(f'{os.getcwd()}/time_stamp.txt', 'r') as f:
        # print(lastDate.strip())
        # print(time.strftime("%Y-%m-%d"))
        # print(lastDate.strip() == time.strftime("%Y-%m-%d"))
        lastDate = f.read()
        #? be CAREFUL of new lines in the time_stamp file. They will stop this function from terminating early here
        if lastDate.strip() == time.strftime("%Y-%m-%d"):
            print(f'{__file__}: already ran this')
            return

    # mark to prevent another run on the same day
    with open(f'{os.getcwd()}/time_stamp.txt', 'w') as f:
        f.write(time.strftime("%Y-%m-%d"))

    FILENAMES = ['levoit_air_filters_multithread', 'ryzen_7_3700x_multithread']

    Path(f'{Path.cwd()}/CSVFiles').mkdir(parents=True, exist_ok=True)

    search_terms = [
        ('B08H8QNW1S', FILENAMES[0]),
        ("B07SXMZLPK", FILENAMES[1]),
    ]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(process_query, search_terms)

    # filter out rows that aren't the desired products
    RYZEN_CPU = 'AMD Ryzen 7 3700X 8-Core, 16-Thread Unlocked Desktop Processor with Wraith Prism LED Cooler'
    AIR_FILTER_DESC = 'LEVOIT LV-H128 Air Purifier Replacement, 3-in-1 Pre-Filter, H13 True HEPA, Activated Carbon, 3-Stage Filtration System, 2 Piece Set, LV-H128-RF, 1 Pack'

    filterCSV(f'{os.getcwd()}/CSVFiles/{FILENAMES[0]}.csv', AIR_FILTER_DESC)
    filterCSV(f'{os.getcwd()}/CSVFiles/{FILENAMES[1]}.csv', RYZEN_CPU)
    send_message(f'finished collecting amazon product data for today: {time.strftime("%Y-%m-%d")}')


if __name__ == '__main__':
    main()

