# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class DealsdirectItem(Item):
    # define the fields for your item here like:
    title = Field()
    product_id = Field()
    sku = Field()
    price = Field()
    price_original = Field()
    quantity = Field()
    description_title = Field()
    description = Field()
    url = Field()
    category1 = Field()
    category2 = Field()
