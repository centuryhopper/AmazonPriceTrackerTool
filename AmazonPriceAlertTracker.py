import requests
from bs4 import BeautifulSoup
import unicodedata
from secrets import Secrets

HEADERS = ({'User-Agent':
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})

#region getProductInfo(url)
def getProductInfo(url):
    page = requests.get(url, headers=HEADERS)
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
#endregion

#region processAmazonLinks(urls)
def processAmazonLinks(products):
    pass
    products_below_limit = []
    for product_url, priceLimit in products:
        title, price, available = getProductInfo(product_url)
        if title is not None and price < priceLimit and available:
            products_below_limit.append((product_url, title, price, priceLimit))
    if products_below_limit:
        message = "Subject: Price below limit!\n\n"
        message += "Your tracked products are below the given limit!\n\n"
        for url, title, price, priceLimit in products_below_limit:
            message += f"{title}\n"
            message +=f"Your customized price limit: ${priceLimit}\n"
            message += f"Price scraped from online: ${price}\n"
            message += f"{url}\n\n"
        Secrets.sendEmail('', '', Secrets.EmailCredentials(sender=Secrets.senderEmail, recipients=Secrets.receiverEmails,password=Secrets.senderEmailPassword), 'Price Drop from Amazon!', message)
    # print(products_below_limit)

#endregion

if __name__ == '__main__':
    products = [
        ("https://www.amazon.com/QNAP-TS-230-Cortex-A53-Quad-core-Processor/dp/B083W6328Q/ref=sr_1_1?keywords=qnap%2Bts230&qid=1638930694&sr=8-1&th=1", 180),
        ]
    processAmazonLinks(products)
    pass
