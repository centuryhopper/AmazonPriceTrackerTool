from requests_html import HTMLSession
from colorama import Fore, Back, Style
import csv
import datetime as dt
import sqlite3


# create a folder named db (if it doesn't already exist already and connect to/create database
conn = sqlite3.connect('./db/amazon_product_info.db')
c = conn.cursor()

# dontexecutethisline.execute('''DROP TABLE IF EXISTS prices''')

# region DO NOT UNCOMMENT CONTENTS WITHIN THIS REGION IF YOU HAVE ALREADY CREATED THIS TABLE
# Again, only create the table once, then comment out or delete the line
# c.execute('''CREATE TABLE prices(date DATE, asin TEXT, price FLOAT, title TEXT)''')
# endregion

# start session and create lists
s = HTMLSession()

# collection of Amazon Standard Identification Numbers
asins = []

# read csv to list
with open('asins.csv', 'r') as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
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
    except Exception as e:
        try:
            price = r.html.find('#priceblock_ourprice')[0].text.replace(
                '$', '').replace(',', '').strip()
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
