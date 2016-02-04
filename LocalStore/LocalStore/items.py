# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class StoreItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = Field()
    name = Field()
    phone = Field()
    #address = Field()
    street_address = Field()
    shopping_centre = Field()
    suburb = Field()
    state = Field()
    postcode = Field()
    brand = Field()
    website = Field()
    categories = Field()
    opentime = Field()

class SuburbItem(Item):
    id = Field()
    name = Field()
    state = Field()
    postcode = Field()

class CategoryItem(Item):
    id = Field()
    name = Field()

class BrandItem(Item):
    id = Field()
    name = Field()
    image = Field()