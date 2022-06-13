import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
import os
import time
import io

# Set working directory to project file
os.chdir(os.path.dirname(__file__))
print(os.getcwd())
# Define the search function that will locate the desired item
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
    chrome_options = Options()
    # chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options = chrome_options)
    records = []
    url = search(item[0])
    for page in range(1,7):
        driver.get(url.format(page))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        results = soup.find_all('div',{'data-component-type':"s-search-result"})

        for i in results:
            record = extract(i)
            if record:
                records.append(record)
    print(f'records: {records}')
    filePathComplete = "{}/CSVFiles/{}.csv".format(os.getcwd(), item[1])
    # print(records)

    with open(filePathComplete, 'a', newline= '', encoding = 'utf-8') as file:
        writer = csv.writer(file)
        if os.stat(filePathComplete).st_size == 0:
            writer.writerow(['Date','Description','Price','Rating','Review Count', 'URL'])
        writer.writerows(records)
    driver.quit()

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
        lastDate = f.read()
        # print(lastDate, time.strftime("%Y-%m-%d"))
        # print(lastDate == time.strftime("%Y-%m-%d"))
        if lastDate == time.strftime("%Y-%m-%d"):
            print('already ran this')
            return

    # mark to prevent another run on the same day
    with open(f'{os.getcwd()}/time_stamp.txt', 'w') as f:
        f.write(time.strftime("%Y-%m-%d")+'\n')

    for search_term in search_terms:
        process_query(search_term)


    # filter out rows that aren't the desired products
    NAS_DESC = 'QNAP TS-230 2-Bay Home NAS Realtek RTD1296 ARM Cortex-A53 Quad-core 1.4 GHz Processor, 2GB DDR4 RAM'
    AIR_FILTER_DESC = 'LEVOIT Air Purifier Replacement LV-H128-RF 3-in-1 Pre, H13 True HEPA, Activated Carbon, 3-Stage Filtration System, 2 Piece Set, LV-H128 Filter'
    filterCSV('./CSVFiles/qnap_network_drive.csv', NAS_DESC)
    filterCSV('./CSVFiles/levoit_air_filters.csv', AIR_FILTER_DESC)

# search_term = input('What would you like to search Amazon for? ')
# main(search_term)

search_terms = [
    ("B083W6328Q", 'qnap_network_drive'),
    ('B08H8QNW1S', 'levoit_air_filters')
]

if __name__ == '__main__':
    main()

