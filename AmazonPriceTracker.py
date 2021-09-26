from requests_html import HTMLSession
from colorama import Fore, Back, Style
import csv
import datetime as dt
import sqlite3
from sqlite3 import OperationalError

# dontexecutethisline.execute('''DROP TABLE IF EXISTS prices''')

#region startPriceTracking
def startPriceTracking():
    # create a folder named db (if it doesn't already exist already and connect to/create database
    conn = sqlite3.connect('./db/amazon_product_info.db')
    c = conn.cursor()

    try:
        c.execute('''SELECT * FROM prices''')
    except OperationalError as o:
        print(o)
        print('therefore creating one now')
        c.execute('''CREATE TABLE prices(date DATE, asin TEXT, price FLOAT, title TEXT)''')


    # start session and create lists
    s = HTMLSession()

    # collection of Amazon Standard Identification Numbers
    asins = []

    # read csv to list
    with open('asins.csv', 'r') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            # append the first column of every row
            asins.append(row[0])

    # scrape data
    for asin in asins:
        r = s.get(f'https://www.amazon.com/dp/{asin}')
        # print(asins)
        r.html.render(sleep=1)
        # print(Fore.RED, end='')
        # print(Back.YELLOW, asins)
        # print(Style.RESET_ALL, end='')
        try:
            price = r.html.find('#price_inside_buybox')[0].text.replace(
                '$', '').replace(',', '').strip()
            # print(f'PRICE: {price}')
        except Exception as e:
            try:
                price = r.html.find('#priceblock_ourprice')[0].text.replace(
                    '$', '').replace(',', '').strip()
                # print(f'PRICE (nested): {price}')
            except Exception as e:
                print(e)
                break
        # cast as a float in case we need it down the road for comparing
        price = float(price)
        title = r.html.find('#productTitle')[0].text.strip()
        date = dt.datetime.today()
        c.execute('''INSERT INTO prices VALUES(?,?,?,?)''',
                (date, asin, price, title))
        print(f'Added data for {title} with asin: {asin}, price: {price}')

    # finalize changes into the database
    conn.commit()
    print('Committed new entries to database')
#endregion


startPriceTracking()
