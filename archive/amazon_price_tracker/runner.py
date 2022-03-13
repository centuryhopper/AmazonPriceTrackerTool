import subprocess
import scrapy
from scrapy.crawler import CrawlerProcess



if __name__ == '__main__':
    # subprocess.run("scrapy crawl AmazonProduct".split())
    process = CrawlerProcess()
    process.crawl(AmazonproductSpider)
    process.start()

