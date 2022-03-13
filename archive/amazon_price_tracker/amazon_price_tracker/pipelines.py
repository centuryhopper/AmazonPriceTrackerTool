# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import csv
import os



class AmazonPriceTrackerPipeline:
    def process_item(self, item, spider):

        if not os.path.isdir("ResultFiles/"):
            os.mkdir("ResultFiles/")

        filename = "ResultFiles/" + item['category'] + '.csv'

        with open(filename, 'a') as f:
            writer = csv.writer(f)
            row = [item['title'], item['price'], item['date_time']]
            writer.writerow(row)


        return item
