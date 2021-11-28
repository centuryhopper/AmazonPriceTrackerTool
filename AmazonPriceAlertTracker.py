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
        ("https://www.amazon.com/gp/product/B07D75MVX9/ref=ox_sc_act_title_1?smid=A1KWJVS57NX03I&psc=1", 170),
        ("https://www.amazon.com/SAMSUNG-50-Inch-Class-QLED-Built/dp/B08VW4GBVJ?ref_=Oct_DLandingS_D_3324dfc1_66&smid=ATVPDKIKX0DER&th=1", 628),
        ]
    processAmazonLinks(products)
    pass
