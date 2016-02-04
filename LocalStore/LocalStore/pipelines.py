# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from LocalStore.items import SuburbItem, StoreItem
from scrapy.exceptions import DropItem
import pymysql

class LocalstorePipeline(object):

    def __init__(self):
        self.conn = pymysql.connect(host='10.0.0.176',
                                    user='shop',
                                    password='nohack',
                                    db='localstore',
                                    charset='utf8mb4',
                                    cursorclass=pymysql.cursors.DictCursor)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        if isinstance(item, SuburbItem):
            item = self.process_suburb(item, spider)
        else:
            item = self.process_store(item, spider)

        return item

    def process_suburb(self, item, spider):
        if self._is_existing(item['id'], 'suburbs', spider):
            raise DropItem("Duplicate suburb found: %s" % item['id'])

        sql = "INSERT into suburbs (`id`,`name`,`state`) values (%s,%s,%s);"

        try:
            self.cursor.execute(sql,[
                item['id'],
                item['name'],
                item['state'],
            ])
            self.conn.commit()
        except pymysql.Error, e:
            print (e)

        return item

    def process_store(self, item, spider):
        if self._is_existing(item['id'], 'stores', spider):
            raise DropItem("Duplicate store found: %s" % item['id'])

        # prepare data
        if item['categories']:
            categories_str = '|'.join(key for key,value in item['categories'].items())
        else:
            categories_str = ''

        if item['brand']:
            brand_str = item['brand'][0].iterkeys().next()
        else:
            brand_str = ""

        # insert brand
        sql_brand = "replace into brands (`id`, `name`, `image`) values (%s,%s,%s);"

        sql_cat = "replace into categories (`id`, `name`) values (%s,%s);"

        sql = "INSERT into stores (`id`,`name`,`phone`,`street_address`,`shopping_centre`,`suburb`,`state`,`postcode`,`brand`,`website`,`categories`,`opentime`) " \
              "values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"


        try:
            if item['brand']:
                self.cursor.execute(sql_brand,[brand_str, item['brand'][0][brand_str], item['brand'][1]['img']])
                #spider.logger.info(self.cursor._last_executed)
            if item['categories']:
                for c_key, c_value in item['categories'].items():
                    self.cursor.execute(sql_cat,[c_key,c_value])

            self.cursor.execute(sql,[
                item['id'],
                item['name'],
                item['phone'],
                item['street_address'],
                item['shopping_centre'],
                item['suburb'],
                item['state'],
                item['postcode'],
                brand_str,
                item['website'],
                categories_str,
                item['opentime']
            ])

            self.conn.commit()
            #spider.logger.info(self.cursor._last_executed)
        except pymysql.Error, e:
            spider.logger.info(self.cursor._last_executed)
            print (e)
        return item

    # @type 'brands', 'categories', 'stores', 'suburbs'
    def _is_existing(self, id, type, spider):
        type_list = ['brands', 'categories', 'stores', 'suburbs']

        if type in type_list:
            stat = "Select * from `%s` where id = %s;" % (type, id)
            try:
                self.cursor.execute(stat)
                result = self.cursor.fetchone()
            except pymysql.Error:
                #spider.logger.info(self.cursor._last_executed)
                return False;
        else:
            return False

        if result:
            return True
        else:
            return False

    def spider_closed(self, spider):
         self.conn.close()