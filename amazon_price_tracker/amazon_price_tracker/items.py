# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

# run in terminal: scrapy shell 'https://www.amazon.com/s?k=nas&page=1&i=electronics&crid=2VM73XGJEYW&sprefix=nas%2Celectronics%2C90&ref=nb_sb_noss'
# https://www.amazon.com/dp/B083W6328Q

class AmazonPriceTrackerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
