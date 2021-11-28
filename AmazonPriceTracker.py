import requests
import csv
import datetime as dt
import sqlite3
import random as rand
from bs4 import BeautifulSoup
from selenium import webdriver
from colorama import Fore, Back, Style
from sqlite3 import OperationalError
from secrets import *

# region getUrl


def getUrl(searchTerm):
    '''Generate a url from the search term param'''
    pass
    searchTerm = searchTerm.replace(' ', '+')
    template = f"https://www.amazon.com/s?k={searchTerm}&ref=nb_sb_noss"
    return template

# endregion

# region extractRecord
def extractRecord(itemToParse) -> list:
    '''Extract the desired information from a single record to parse'''
    pass
    atag = itemToParse.h2.a
    # print(atag.text)
    title = atag.text
    # print(atag.get('href'))
    url = 'https://amazon.com' + atag.get('href')
    try:
        # we only want this record if there's a price available
        priceParent = itemToParse.find('span', 'a-price')
        price = priceParent.find('span', 'a-offscreen').text
        # print(type(price),price)
        # price = float(itemToParse.find('span', 'a-price-whole').text)
    except AttributeError:
        return None
    # print(price)
    return (dt.datetime.now().strftime("%I:%M%p on %B %d, %Y"), title, f'{price}', f"{url}",)

# endregion

# region collectData


def collectData(searchTerm=''):
    '''get date, price, title, and url to that item'''
    pass
    driver = webdriver.Chrome(CHROME_DRIVER_PATH)
    url = getUrl(searchTerm)
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # get all search results on the current page
    res = soup.find_all('div', {'data-component-type': 's-search-result'})
    # just get the results on the first page
    # might get the results from succeeding pages down the road, if needed
    records = [extractRecord(record)
               for record in res if extractRecord(record)]
    # print(records)
    driver.close()
    appendToFile(records)

# endregion

# region isCSVEmpty


def isCSVEmpty(path):
    with open(path) as f:
        reader = csv.reader(f)
        for i, _ in enumerate(reader):
            if i:  # found the second row
                return False
    return True

# endregion

# region appendFile


def appendToFile(records=[], relativeFilePath=True):
    pass
    filePath = './files/AmazonItemRecords.csv' if relativeFilePath else csvFilePath
    with open(filePath, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if isCSVEmpty(filePath):
            print('this is a brand new csv file, so adding headers to it now')
            writer.writerow(['Date', 'Title', 'Price', 'Item_URL'])
        writer.writerows(records)

# endregion


if __name__ == '__main__':
    searchQueries = [
        'Plugable USB 3.0 and USB-C Universal Laptop Docking Station for Windows and Mac (Dual Video HDMI, Gigabit Ethernet, Audio, 6 USB Ports)',
        'Logitech K780 Multi-Device Wireless Keyboard for Computer, Phone and Tablet – FLOW Cross-Computer Control Compatible – Speckles',
        'Sceptre E248W-19203R 24" Ultra Thin 75Hz 1080p LED Monitor 2x HDMI VGA Build-in Speakers, Metallic Black 2018',
        'Sceptre New 22 Inch FHD LED Monitor 75Hz 2X HDMI VGA Build-in Speakers, Machine Black (E22 Series)',
    ]

    for searchQuery in searchQueries:
        collectData(searchQuery)

































# dontexecutethisline.execute('''DROP TABLE IF EXISTS prices''')
# region startPriceTracking (deprecated code)
# def startPriceTracking():
# create a folder named db (if it doesn't already exist already and connect to/create database
# conn = sqlite3.connect('./db/amazon_product_info.db')
# c = conn.cursor()
# try:
#     c.execute('''SELECT * FROM prices''')
# except OperationalError as o:
#     print(o)
#     print('therefore creating one now')
#     c.execute('''CREATE TABLE prices(date DATE, asin TEXT, price FLOAT, title TEXT)''')
# # collection of Amazon Standard Identification Numbers
# asins = None
# # read csv to list
# with open('asins.csv', 'r') as f:
#     csv_reader = csv.reader(f)
#     # append the first column of every row
#     asins = [row[0] for row in csv_reader]
# # print(asins)
# scrape data
# for asin in asins:
#     page = requests.get(f'https://www.amazon.com/dp/{asin}')
#     print(page.text)
#     # if page.status_code != 200:
#     #     print(f'error code: {page.status_code}. Unable to load webpage with asin: {asin}')
#     #     continue
#     soup = BeautifulSoup(page.content, 'html.parser')
#     print(soup.children)
#     break
# print(Fore.RED, end='')
# print(Back.YELLOW, asins)
# print(Style.RESET_ALL, end='')
# try:
#     price = r.html.find('newBuyBoxPrice')[0].text.replace(
#         '$', '').replace(',', '').strip()
#     # print(f'PRICE: {price}')
# except Exception as e:
#     print(e)
#     try:
#         price = r.html.find('priceblock_ourprice')[0].text.replace(
#             '$', '').replace(',', '').strip()
#         # print(f'PRICE (nested): {price}')
#     except Exception as e:
#         print('something went wrong')
#         break
# # cast as a float in case we need it down the road for comparing
# price = float(price)
# title = r.html.find('#productTitle')[0].text.strip()
# date = dt.datetime.today()
# c.execute('''INSERT INTO prices VALUES(?,?,?,?)''',
#         (date, asin, price, title))
# print(f'Added data for {title} with asin: {asin}, price: {price}')
# finalize changes into the database
# conn.commit()
# print('Committed new entries to database')
# endregion
