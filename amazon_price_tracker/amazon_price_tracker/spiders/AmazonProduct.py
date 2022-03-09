import scrapy
from time import strftime
from ..items import AmazonPriceTrackerItem

class AmazonproductSpider(scrapy.Spider):
    name = 'AmazonProduct'
    allowed_domains = ['amazon.com']
    start_urls = [
        'https://www.amazon.com/dp/B083W6328Q',
        'https://www.amazon.com/dp/B07RGPCQG1']

    def parse(self, response):
        product = AmazonPriceTrackerItem()
        title = response.css('.a-size-large.product-title-word-break::text').extract_first()
        price = response.css('.a-price-whole::text').extract_first()
        date_time = strftime("%Y%m%d-%H%M")
        product['title'] = title
        product['price'] = price
        product['date_time'] = date_time
        yield product
