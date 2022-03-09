import requests
from bs4 import BeautifulSoup
import unicodedata
import pandas as pd
from secrets import Secrets
from time import strftime
from collections import defaultdict
# from prophet import Prophet
# from prophet.plot import plot_plotly, plot_components_plotly
# import matplotlib.pyplot as plt
import os
import platform


# Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.109 Safari/537.36
HEADERS = ({'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})

if platform.system() == 'Darwin':
    HEADERS = {
            'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.109 Safari/537.36',
        }

proxies = {
  "http": None,
  "https": None,
}

soup = None

def getProductInfo(url):
    global soup
    page = requests.get(url, headers=HEADERS, proxies=proxies)
    print(page.status_code)
    soup = BeautifulSoup(page.content, features="lxml")
    try:
        title = soup.find('span',{'id':'productTitle'}).get_text().strip()
        price_str = soup.find('div',{'id':'corePrice_feature_div'})
        price_str = price_str.find('span',{'aria-hidden':'true'}).get_text().strip()
    except:
        return None, None, None
    try:
        # #soup.select('#availability .a-color-price')[0].get_text().strip()
        soup.select('#availability .a-color-success')[0].get_text().strip()
        available = True
    except:
        available = False
    try:
        price = unicodedata.normalize("NFKD", price_str)
        price = price.replace(',', '.').replace('$', '')
        price = float(price)
    except:
        return None, None, None
    return title, price, available


def processAmazonLinks(products):
#region
    def appendToCSV(df,filePath):
        # if file does not exist write header
        if not os.path.isfile(filePath):
            df.to_csv(filePath,index=False)
        else: # else it exists so append without writing the header
            df.to_csv(filePath, index=False, mode='a', header=False)

#endregion

    curDateTime = strftime("%Y%m%d-%H%M")
    products_below_limit = []
    d = defaultdict(list)
    for product_title, product_url, priceLimit in products:
        title, price, available = getProductInfo(product_url)
        fileName = f'{product_title}.csv'
        filePath = Secrets.WINDOWS_CSV_PATH + fileName
        if platform.system() == 'Darwin':
            filePath = Secrets.MAC_CSV_PATH + fileName
        print(title, price, available)
        if title is not None and price < priceLimit and available:
            d['title'].append(title)
            d['price'].append(price)
            d['datetime'].append(curDateTime)
            products_below_limit.append((product_url, title, price, priceLimit))
            df = pd.DataFrame(d)
            print(df)
            appendToCSV(df, filePath)
            d.clear()

    # TODO: include in the email for when a price drop will occur in the future
    # if products_below_limit:
    #     message = "Subject: Price below limit!\n\n"
    #     message += "Your tracked products are below the given limit!\n\n"
    #     for url, title, price, priceLimit in products_below_limit:
    #         message += f"{title}\n"
    #         message +=f"Your customized price limit: ${priceLimit}\n"
    #         message += f"Price scraped from online: ${price}\n"
    #         message += f"{url}\n\n"
    #     Secrets.sendEmail('', '', Secrets.EmailCredentials(sender=Secrets.senderEmail, recipients=Secrets.receiverEmails,password=Secrets.senderEmailPassword), 'Price Drop from Amazon!', message)


if __name__ == '__main__':
    # https://www.amazon.com/dp/B083W6328Q
    # https://www.amazon.com/dp/B07RGPCQG1
    # "https://www.amazon.com/QNAP-TS-230-Cortex-A53-Quad-core-Processor/dp/B083W6328Q/ref=sr_1_1?keywords=qnap%2Bts230&qid=1638930694&sr=8-1&th=1"

    products = [
    ("qnap_network_drive","https://www.amazon.com/dp/B083W6328Q", 200),
    ("portable_monitor","https://www.amazon.com/dp/B07RGPCQG1", 220),
    ]
    processAmazonLinks(products)

    # Time series
    #? Note that the csv files must have as many different dates as possible. If all the dates are the same, then there wont be any predictions

    # for title,_,_ in products:
    #     filePath = f'C:\\Users\\Leo Zhang\\Documents\GitHub\\PythonAmazonPriceTracker\\CSVFiles\\{title}.csv'
    #     if not os.path.isfile(filePath): continue
    #     df = pd.read_csv(f'./CSVFiles/{title}.csv')
    #     df['Year'] = df['datetime'].apply(lambda x: str(x)[:4])
    #     df['Month'] = df['datetime'].apply(lambda x: str(x)[4:6])
    #     df['Day'] = df['datetime'].apply(lambda x: str(x)[6:8])
    #     df['ds'] = pd.DatetimeIndex(df['Year']+'-'+df['Month']+'-'+df['Day'])
    #     # axis = 1 for columns, 0 for rows
    #     df.drop(['datetime','Year','Month','Day', 'title'], axis=1, inplace=True)
    #     df.rename(columns={'price':'y'}, inplace=True)
    #     df.reset_index(drop=True,inplace=True)
        # print(df)
        # print(df.dtypes)

        # m = Prophet(weekly_seasonality=True)
        # model = m.fit(df)
        # # forecast 14 days into the future
        # future = m.make_future_dataframe(periods=14)
        # forecast_df = m.predict(future)
        # print(forecast_df.head(10))
        # print(forecast_df.tail(10))
        # print()

#region test code
    # df = pd.read_csv('./CSVFiles/dummy.csv')
    # df['Year'] = df['Time Date'].apply(lambda x: str(x)[-4:])
    # df['Month'] = df['Time Date'].apply(lambda x: str(x)[-6:-4])
    # df['Day'] = df['Time Date'].apply(lambda x: str(x)[:-6])
    # df['ds'] = pd.DatetimeIndex(df['Year']+'-'+df['Month']+'-'+df['Day'])
    # df = df.loc[(df['Product']==2667437) & (df['Store']=='QLD_CW_ST0203')]
    # df.drop(['Time Date', 'Product', 'Store', 'Year', 'Month', 'Day'], axis=1, inplace=True)
    # df.columns = ['y', 'ds']

    # print(df)

    # m = Prophet(interval_width=0.95,daily_seasonality=True)
    # model = m.fit(df)
    # # forecast 365 days into the future
    # future = m.make_future_dataframe(periods=365, freq='D')
    # forecast_df = m.predict(future)
    # print(forecast_df.head(10))
    # print(forecast_df.tail(10))
    # fig1 = m.plot(forecast_df)
    # fig2 = m.plot_components(forecast_df)
    # plt.show()

#endregion




