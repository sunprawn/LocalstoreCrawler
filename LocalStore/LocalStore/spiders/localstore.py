# -*- coding: utf-8 -*-
import scrapy


class LocalstoreSpider(scrapy.Spider):
    name = "localstore"
    allowed_domains = ["localstore.com.au", "www.localstore.com.au"]
    start_urls = [
        'http://www.localstore.com.au/browse/regions/%s/' % s
        for s in "a"#"abcdefghijklmnopqrstuvwxyz"
    ]

    def parse(self, response):
        content = response.xpath('//table[contains(@class, "main_content")]//table//table//table//tbody')

