import scrapy
from time import strftime
from ..items import AmazonPriceTrackerItem
import re

# scrapy shell 'your url goes here' to debug response object in the terminal
# scrapy crawl AmazonProduct (just to display the information in the terminal)
class AmazonproductSpider(scrapy.Spider):
    name = 'AmazonProduct'
    allowed_domains = ['amazon.com']
    start_urls = [
        'https://www.amazon.com/dp/B083W6328Q',
        'https://www.amazon.com/dp/B07RGPCQG1',
    ]

    def parse(self, response):
        product = AmazonPriceTrackerItem()
        title = response.css('span.a-size-large.product-title-word-break::text').extract_first()
        price = response.css('span.a-price-whole::text').extract_first()
        date_time = strftime("%Y%m%d-%H%M")
        product['title'] = title.strip() if title else 'N/A'
        product['price'] = price
        product['date_time'] = date_time

        x = re.search("dp\/(.*)", response.url)
        product['category'] = x.group(1)
        yield product



