import concurrent.futures
import csv
import os
import time

import pandas as pd
from bs4 import BeautifulSoup
from fake_useragent import FakeUserAgentError, UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from contextlib import contextmanager


# { time python3 AmazonScraperMultithread.py; } &> res.txt
ua = None
while True:
    try:
        ua = UserAgent()
        break
    except FakeUserAgentError:
        print('fake user agent error')
        continue
    except Exception:
        continue

fake_agent = ua.random

# Set working directory to project file
os.chdir(os.path.dirname(__file__))
# print(os.getcwd())
# Define the search function that will locate the desired item

@contextmanager
def driver(*args, **kwargs):
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--start-fullscreen')
    chrome_options.add_argument('--single-process')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_argument("--headless")
    chrome_options.add_argument(f'user-agent={fake_agent}')
    chrome_options.add_argument('--ignore-ssl-errors=yes')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")

    d = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options,)
    d.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    d.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source":
            "const newProto = navigator.__proto__;"
            "delete newProto.webdriver;"
            "navigator.__proto__ = newProto;"
    })

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
        # print(records)

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

    print('here')

    search_terms = [
        ("B083W6328Q", 'qnap_network_drive_multithread'),
        ('B08H8QNW1S', 'levoit_air_filters_multithread'),
        ("B08V83JZH4", 'samsung_980_1tb_nvme_ssd_multithread'),
        ("B08GLX7TNT", "samsung_980_pro_1tb_nvme_ssd_multithread"),
    ]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(process_query, search_terms)

    # filter out rows that aren't the desired products
    NAS_DESC = 'QNAP TS-230 2-Bay Home NAS Realtek RTD1296 ARM Cortex-A53 Quad-core 1.4 GHz Processor, 2GB DDR4 RAM'
    AIR_FILTER_DESC = 'LEVOIT Air Purifier Replacement LV-H128-RF 3-in-1 Pre, H13 True HEPA, Activated Carbon, 3-Stage Filtration System, 2 Piece Set, LV-H128 Filter'
    SAMSUNG_980_EVO = 'SAMSUNG 980 SSD 1TB M.2 NVMe Interface Internal Solid State Drive with V-NAND Technology for Gaming, Heavy Graphics, Full Power Mode, MZ-V8V1T0B/AM'
    SAMSUNG_980_PRO_EVO = 'SAMSUNG 980 PRO SSD 1TB PCIe 4.0 NVMe Gen 4 Gaming M.2 Internal Solid State Hard Drive Memory Card, Maximum Speed, Thermal Control, MZ-V8P1T0B'


    filterCSV(f'{os.getcwd()}/CSVFiles/qnap_network_drive_multithread.csv', NAS_DESC)
    filterCSV(f'{os.getcwd()}/CSVFiles/levoit_air_filters_multithread.csv', AIR_FILTER_DESC)
    filterCSV(f'{os.getcwd()}/CSVFiles/samsung_980_1tb_nvme_ssd_multithread.csv', SAMSUNG_980_EVO)
    filterCSV(f'{os.getcwd()}/CSVFiles/samsung_980_pro_1tb_nvme_ssd_multithread.csv', SAMSUNG_980_PRO_EVO)


if __name__ == '__main__':
    main()

