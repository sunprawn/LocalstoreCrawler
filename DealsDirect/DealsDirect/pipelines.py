# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from scrapy.exceptions import DropItem

class DealsdirectPipeline(object):
    def process_item(self, item, spider):
        return item

class MysqlPipeline(object):
    def __init__(self):
        self.conn = pymysql.connect(host='10.0.0.176',
                                    user='shop',
                                    password='nohack',
                                    db='dealsdirect',
                                    charset='utf8mb4',
                                    cursorclass=pymysql.cursors.DictCursor)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):

        #spider.logger.info(type(item['product_id']))
        is_product = self._is_product(item['product_id'])

        if is_product:
            self._insert_trend(item)
            raise DropItem("Duplicate product found: %d" % item['product_id'])

        sql = "INSERT INTO products (`id`,`sku`,`title`,`url`,`category1`,`category2`,`description_title`,`description`) values (%s,%s,%s,%s,%s,%s,%s,%s);"

        try:
            self.cursor.execute(sql,[
                item['product_id'],
                item['sku'],
                item['title'],
                item['url'],
                item['category1'],
                item['category2'],
                item['description_title'],
                item['description'],
            ])
            self.conn.commit()
        except pymysql.Error, e:
            print (e)

        self._insert_trend(item)

        return item

    def spider_closed(self, spider):
         self.conn.close()

    def _insert_trend(self, item):
        # if product is out of stock
        if item['quantity'] == 0:
            item['price'] = 0
            item['price_original'] = 0

        # get the trend to compare
        sql = "select product_id, price, price_original, quantity from trend where product_id = %s order by datetime desc limit 1"
        try:
            self.cursor.execute(sql, [item['product_id']])
            result = self.cursor.fetchone()

        except pymysql.Error:
            return

        # if the record exists since last insert, do not insert
        if result and \
                result['product_id'] == item['product_id'] and \
                result['price'] == item['price'] and \
                result['price_original'] == item['price_original'] and \
                result['quantity'] == item['quantity']:
            return

        # insert the trend detail
        sql = "INSERT INTO trend (`product_id`,`price`,`price_original`,`quantity`) values (%s,%s,%s,%s);"
        try:
            self.cursor.execute(sql,[
                item['product_id'],
                item['price'],
                item['price_original'],
                item['quantity'],
            ])
            self.conn.commit()
        except pymysql.Error, e:
            print (e)


    def _is_product(self, pid):
        stat = "Select * from products where id = %s"
        try:
            self.cursor.execute(stat, [pid])
            result = self.cursor.fetchone()
        except pymysql.Error:
            return False;


        if result:
            return True
        else:
            return False
