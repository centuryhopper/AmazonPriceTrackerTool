import requests
from bs4 import BeautifulSoup
import unicodedata
import pandas as pd
from prophet import Prophet
from secrets import Secrets
from time import strftime
from collections import defaultdict
from prophet.plot import plot_plotly, plot_components_plotly


HEADERS = ({'User-Agent':
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})

#region getProductInfo(url)
def getProductInfo(url):
    page = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(page.content, features="html.parser")
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
#endregion

#region processAmazonLinks(urls)
def processAmazonLinks(products):
    curDateTime = strftime("%Y%m%d-%H%M")
    fileName = f'AmazonPriceAlerts.csv'
    filePath = f'C:\\Users\\Leo Zhang\\Documents\GitHub\\PythonAmazonPriceTracker\\CSVFiles\\{fileName}'
    products_below_limit = []
    d = defaultdict(list)
    for product_url, priceLimit in products:
        title, price, available = getProductInfo(product_url)
        # print(title,price,available)
        if title is not None and price < priceLimit and available:
            d['title'].append(title)
            d['price'].append(price)
            d['datetime'].append(curDateTime)
            products_below_limit.append((product_url, title, price, priceLimit))
        # print(d)
    if products_below_limit:
        df = pd.DataFrame(d)
        df.to_csv(filePath, index=False, mode='a', header=False)
        message = "Subject: Price below limit!\n\n"
        message += "Your tracked products are below the given limit!\n\n"
        for url, title, price, priceLimit in products_below_limit:
            message += f"{title}\n"
            message +=f"Your customized price limit: ${priceLimit}\n"
            message += f"Price scraped from online: ${price}\n"
            message += f"{url}\n\n"
        Secrets.sendEmail('', '', Secrets.EmailCredentials(sender=Secrets.senderEmail, recipients=Secrets.receiverEmails,password=Secrets.senderEmailPassword), 'Price Drop from Amazon!', message)

#endregion

if __name__ == '__main__':
    # products = [
    #     ("https://www.amazon.com/QNAP-TS-230-Cortex-A53-Quad-core-Processor/dp/B083W6328Q/ref=sr_1_1?keywords=qnap%2Bts230&qid=1638930694&sr=8-1&th=1", 200),
    #     ]
    # processAmazonLinks(products)

    df = pd.read_csv('./CSVFiles/dummy.csv')
    df['Year'] = df['Time Date'].apply(lambda x: str(x)[-4:])
    df['Month'] = df['Time Date'].apply(lambda x: str(x)[-6:-4])
    df['Day'] = df['Time Date'].apply(lambda x: str(x)[:-6])
    df['ds'] = pd.DatetimeIndex(df['Year']+'-'+df['Month']+'-'+df['Day'])
    df = df.loc[(df['Product']==2667437) & (df['Store']=='QLD_CW_ST0203')]
    df.drop(['Time Date', 'Product', 'Store', 'Year', 'Month', 'Day'], axis=1, inplace=True)
    df.columns = ['y', 'ds']
    
    # print(df)
    # df['Year'] = df['datetime'].apply(lambda x: str(x)[:4])
    # df['Month'] = df['datetime'].apply(lambda x: str(x)[4:6])
    # df['Day'] = df['datetime'].apply(lambda x: str(x)[6:8])
    # df['ds'] = pd.DatetimeIndex(df['Year']+'-'+df['Month']+'-'+df['Day'])
    # # axis = 1 for columns, 0 for rows
    # df.drop(['datetime','Year','Month','Day', 'title'], axis=1, inplace=True)
    # df.rename(columns={'price':'y'}, inplace=True)
    # print(df)

    m = Prophet(interval_width=0.95,daily_seasonality=True)
    model = m.fit(df)
    future = m.make_future_dataframe(periods=14, freq='D')
    forecast = m.predict(future)
    # fig1 = m.plot(forecast)
    # fig2 = m.plot_components(forecast)
    plot_plotly(m, forecast)
    plot_components_plotly(m, forecast)




